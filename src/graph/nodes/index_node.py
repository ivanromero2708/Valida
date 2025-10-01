from __future__ import annotations
from pydantic import BaseModel
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from typing import Literal, Any, List
import os
import json
import logging
import tempfile
from pathlib import Path


from src.graph.state import IndexNodeOutput
from src.utils.pathing import resolve_input_path

from langsmith import traceable
from mistralai.extra import response_format_from_pydantic_model
from mistralai import Mistral
import base64
from PyPDF2 import PdfReader, PdfWriter

class DocPathInfo(BaseModel):
    original_path: str
    resolved_path: str

class NodeOutput(BaseModel):
    set_name: str
    extracted_content: List[IndexNodeOutput]

class IndexNodeState(AgentStateWithStructuredResponse):
    set_name: str
    doc_path_list: list[DocPathInfo | dict[str, str] | str]
    data_extraction_model: type[BaseModel]
    extracted_content: list[NodeOutput]


class IndexNode:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_pages_per_chunk = 8  # Mistral OCR limit
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise EnvironmentError("Defina MISTRAL_API_KEY en el entorno")
        self.client = Mistral(api_key=api_key, timeout_ms=300000)

    def _ensure_path(self, value: Path | str | None) -> Path | None:
        if value is None:
            return None
        return Path(value)

    def _extract_paths(self, entry: DocPathInfo | dict[str, str] | str) -> tuple[str | None, Path | None]:
        if isinstance(entry, DocPathInfo):
            original = entry.original_path
            resolved = entry.resolved_path
        elif isinstance(entry, dict):
            original = entry.get("original_path") or entry.get("original") or entry.get("path")
            resolved = entry.get("resolved_path") or entry.get("normalized_path") or entry.get("path")
        else:
            original = str(entry) if entry is not None else None
            resolved = str(entry) if entry is not None else None

        resolved_path = self._ensure_path(resolved) if resolved else None
        return original, resolved_path

    

    def get_pdf_page_count(self, pdf_path: Path | str) -> int:
        """Get the number of pages in a PDF."""
        pdf_path = Path(pdf_path)
        try:
            with open(pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                return len(reader.pages)
        except Exception as e:
            self.logger.error(f"Error counting pages in {pdf_path}: {e}")
            return 0
    
    def split_pdf_into_chunks(self, pdf_path: Path | str) -> list[str]:
        """Split PDF into chunks of max_pages and return temporary file paths."""
        temp_files = []
        pdf_path = Path(pdf_path)
        try:
            with open(pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                for start_page in range(0, total_pages, self.max_pages_per_chunk):
                    end_page = min(start_page + self.max_pages_per_chunk, total_pages)
                    
                    writer = PdfWriter()
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    with open(temp_file.name, "wb") as output_file:
                        writer.write(output_file)
                    
                    temp_files.append(temp_file.name)
                    self.logger.info(f"Created chunk {len(temp_files)}: pages {start_page+1}-{end_page}")
                    
        except Exception as e:
            self.logger.error(f"Error splitting PDF {pdf_path}: {e}")
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
            return []
            
        return temp_files

    def encode_pdf(self, pdf_path: Path | str) -> str:
        """Encode the pdf to base64."""
        pdf_path = Path(pdf_path)
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding PDF {pdf_path}: {e}")
            return None

    @traceable
    def process_chunk(self, pdf_path: Path | str, extraction_model: type[BaseModel]):
        """Process a single PDF chunk with Mistral OCR."""
        try:
            base64_pdf = self.encode_pdf(pdf_path)
            if not base64_pdf:
                return None

            request_params = {
                "model": "mistral-ocr-latest",
                "document": {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}"
                },
                "include_image_base64": False,
            }

            if extraction_model:
                try:
                    request_params["document_annotation_format"] = response_format_from_pydantic_model(extraction_model)
                except Exception as exc:
                    self.logger.warning(f"No se pudo generar schema pydantic para {pdf_path}: {exc}")

            return self.client.ocr.process(**request_params)
        except Exception as e:
            self.logger.error(f"Error processing chunk {pdf_path}: {e}")
            return None
    
    def process_document(self, pdf_path: Path | str, extraction_model: type[BaseModel]) -> list:
        """Process PDF with automatic chunking if needed."""
        pdf_path = Path(pdf_path)
        total_pages = self.get_pdf_page_count(pdf_path)
        self.logger.info(f"Processing PDF {pdf_path} with {total_pages} pages")
        
        if total_pages <= self.max_pages_per_chunk:
            # Process directly if within limit
            result = self.process_chunk(pdf_path, extraction_model)
            return [result] if result else []
        
        # Split into chunks and process each
        chunk_files = self.split_pdf_into_chunks(pdf_path)
        results = []
        
        try:
            for i, chunk_file in enumerate(chunk_files):
                self.logger.info(f"Processing chunk {i+1}/{len(chunk_files)}")
                result = self.process_chunk(chunk_file, extraction_model)
                if result:
                    results.append(result)
        finally:
            # Clean up temporary files
            for chunk_file in chunk_files:
                try:
                    os.unlink(chunk_file)
                except Exception as e:
                    self.logger.warning(f"Could not delete temporary file {chunk_file}: {e}")
        
        return results
    
    
    def consolidate_chunks_data(self, chunk_responses: list, document_name: str, extraction_model: type[BaseModel]):
        """Consolida los document_annotation de todos los chunks y crea una instancia del modelo Pydantic."""
        try:
            if not chunk_responses:
                self.logger.warning(f"No chunks to process for {document_name}")
                return None
            
            # Consolidar todos los datos de los chunks
            all_chunk_data = {}
            
            for i, response in enumerate(chunk_responses):
                if not response:
                    continue
                    
                # Extraer document_annotation del chunk
                annotation_data = None
                if hasattr(response, 'document_annotation'):
                    annotation_data = response.document_annotation
                elif isinstance(response, dict) and 'document_annotation' in response:
                    annotation_data = response['document_annotation']
                
                if annotation_data:
                    try:
                        # Convertir a dict si es necesario
                        if isinstance(annotation_data, str):
                            chunk_data = json.loads(annotation_data)
                        elif isinstance(annotation_data, dict):
                            chunk_data = annotation_data
                        else:
                            chunk_data = json.loads(str(annotation_data))
                        
                        # Mergear datos del chunk con el consolidado
                        self._merge_chunk_data(all_chunk_data, chunk_data)
                        self.logger.debug(f"Merged chunk {i+1} data")
                        
                    except (json.JSONDecodeError, TypeError) as e:
                        self.logger.warning(f"Error parsing chunk {i+1} annotation: {e}")
            
            # Crear instancia del modelo Pydantic con los datos consolidados
            if all_chunk_data and extraction_model:
                try:
                    model_instance = extraction_model(**all_chunk_data)
                    self.logger.info(f"Created {extraction_model.__name__} instance for {document_name}")
                    return model_instance
                except Exception as e:
                    self.logger.error(f"Error creating model instance for {document_name}: {e}")
                    # Fallback: retornar los datos raw
                    return all_chunk_data
            
            self.logger.warning(f"No valid data to create model instance for {document_name}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error consolidating chunks for {document_name}: {e}")
            return None
    
    def _merge_chunk_data(self, target: dict, source: dict):
        """Mergea datos de un chunk con el diccionario consolidado."""
        for key, value in source.items():
            if key in target:
                # Si ambos son listas, concatenar
                if isinstance(target[key], list) and isinstance(value, list):
                    target[key].extend(value)
                # Si ambos son dicts, mergear recursivamente
                elif isinstance(target[key], dict) and isinstance(value, dict):
                    self._merge_chunk_data(target[key], value)
                # Si son del mismo tipo pero no lista/dict, mantener el Ãºltimo valor
                else:
                    target[key] = value
            else:
                target[key] = value
        
    @traceable
    def run(self, state: IndexNodeState, config) -> Command[Literal["op_reasoning_parallelization"]]:
        extraction_content = []

        for entry in state.get("doc_path_list", []):
            original_path, resolved_path = self._extract_paths(entry)

            if resolved_path is None:
                self.logger.warning("Entrada sin ruta resuelta: %s", entry)
                continue

            resolved_path = resolved_path.resolve()
            if not resolved_path.exists():
                fallback = resolve_input_path(original_path or str(resolved_path))
                if fallback and fallback.exists():
                    resolved_path = fallback.resolve()
                else:
                    self.logger.warning(
                        "Documento no encontrado: '%s' (normalizado a '%s')",
                        original_path,
                        resolved_path,
                    )
                    continue

            document_name = Path(original_path).name if original_path else resolved_path.name

            self.logger.info(
                "Processing document: %s (resuelto: %s)",
                original_path or resolved_path.name,
                resolved_path,
            )

            extraction_model = state.get("data_extraction_model")
            chunk_responses = self.process_document(resolved_path, extraction_model)

            model_instance = self.consolidate_chunks_data(chunk_responses, document_name, extraction_model)

            extraction_content.append(
                IndexNodeOutput(
                    document_name=document_name,
                    extracted_content=model_instance
                )
            )

            self.logger.info("Completed processing %s", document_name)

        return Command(
            update={
                "messages": [HumanMessage(content=f"Procesados {len(extraction_content)} documentos.")],
                "extraction_content": [NodeOutput(set_name=state.get("set_name"), extracted_content=extraction_content)]
            },
            goto="op_reasoning_parallelization"
        )

