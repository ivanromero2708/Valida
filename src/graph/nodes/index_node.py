from pydantic import BaseModel, ValidationError
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from langgraph.types import Command
from langchain_core.messages import HumanMessage
from typing import Literal, Any, List, Optional
import os
import json
import logging
import tempfile
import asyncio
import requests
from urllib.parse import urlparse

from dotenv import load_dotenv
load_dotenv()

from src.graph.state import IndexNodeOutput, FileDescriptor
from src.utils.sharepoint_api import SharePointClient

from langsmith import traceable
from mistralai.extra import response_format_from_pydantic_model
from mistralai import Mistral
import base64
from PyPDF2 import PdfReader, PdfWriter


class NodeOutput(BaseModel):
    set_name: str
    extracted_content: List[IndexNodeOutput]


class IndexNodeState(AgentStateWithStructuredResponse):
    set_name: str
    documents: list[FileDescriptor]
    data_extraction_model: type[BaseModel]
    extracted_content: list[NodeOutput]
    doc_path_list: list[str] | None = None





def _coerce_to_descriptor(value: Any) -> FileDescriptor | None:
    if isinstance(value, FileDescriptor):
        return value

    if isinstance(value, dict):
        data = dict(value)

        if not data.get("source") and (
            data.get("siteLookup")
            or data.get("siteUrl")
            or data.get("serverRelativePath")
            or data.get("uniqueId")
        ):
            data["source"] = "sharepoint"

        if not data.get("size"):
            data["size"] = -1

        if not data.get("content_type"):
            content_type = None
            name = data.get("name")
            if isinstance(name, str):
                _, ext = os.path.splitext(name)
                if ext.lower() == ".pdf":
                    content_type = "application/pdf"
            data["content_type"] = content_type or "application/octet-stream"

        if not data.get("name"):
            for candidate in ("filename", "file_name"):
                candidate_val = data.get(candidate)
                if isinstance(candidate_val, str) and candidate_val:
                    data["name"] = candidate_val
                    break
            if not data.get("name"):
                raw_url = data.get("url")
                if isinstance(raw_url, str):
                    data["name"] = os.path.basename(raw_url) or "document.pdf"
                else:
                    data["name"] = "document.pdf"

        try:
            return FileDescriptor(**data)
        except ValidationError as exc:
            logging.getLogger(__name__).warning(
                "No se pudo convertir dict a FileDescriptor: %s", exc
            )
            return None

    if isinstance(value, str):
        name = os.path.basename(value) or value
        return FileDescriptor(
            name=name, url=value, size=-1, content_type="application/octet-stream"
        )
    return None



class IndexNode:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.max_pages_per_chunk = 8  # Mistral OCR limit
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise EnvironmentError("Defina MISTRAL_API_KEY en el entorno")
        self.client = Mistral(api_key=api_key, timeout_ms=300000)
        self._sharepoint_client: Optional[SharePointClient] = None

    def _infer_sharepoint_host(self, descriptor: FileDescriptor) -> Optional[str]:
        for candidate in (descriptor.site_lookup, descriptor.site_url, descriptor.url):
            if not candidate:
                continue
            if ':/' in candidate:
                host = candidate.split(':/', 1)[0].strip()
                if host:
                    return host
            parsed = urlparse(candidate)
            if parsed.netloc:
                return parsed.netloc
        return None

    def _build_sharepoint_download_reference(
        self, descriptor: FileDescriptor, client: SharePointClient
    ) -> str:
        if descriptor.url:
            parsed = urlparse(descriptor.url)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                if parsed.netloc.lower().endswith("graph.microsoft.com"):
                    return descriptor.url
                if "sharepoint" in parsed.netloc.lower():
                    return f"{parsed.netloc}{parsed.path}"
            if descriptor.url.strip():
                return descriptor.url

        server_relative_path = descriptor.server_relative_path
        if server_relative_path:
            normalized = server_relative_path if server_relative_path.startswith('/') else f'/{server_relative_path}'
            site_lookup = (descriptor.site_lookup or "").strip()
            if site_lookup:
                base = site_lookup.rstrip('/')
                return f"{base}{normalized}"
            site_url = (descriptor.site_url or "").strip()
            if site_url:
                parsed_site = urlparse(site_url)
                if parsed_site.netloc:
                    site_path = parsed_site.path.rstrip('/')
                    if site_path:
                        return f"{parsed_site.netloc}:{site_path}{normalized}"
                    return f"{parsed_site.netloc}{normalized}"

        host = self._infer_sharepoint_host(descriptor)
        if host and server_relative_path:
            normalized = server_relative_path if server_relative_path.startswith('/') else f'/{server_relative_path}'
            return f"{host}{normalized}"

        if (
            descriptor.unique_id
            and descriptor.drive_id
            and isinstance(descriptor.unique_id, str)
            and '-' in descriptor.unique_id
        ):
            site_reference = descriptor.site_lookup or descriptor.site_url or host
            if not site_reference:
                raise ValueError("Descriptor SharePoint sin referencia de sitio")
            site_id = client.get_site_id(site_reference)
            resource_base = client.resource_url.rstrip('/')
            return (
                f"{resource_base}/v1.0/sites/{site_id}/drives/{descriptor.drive_id}/"
                f"items/{descriptor.unique_id}/content"
            )

        raise ValueError(
            f"No se pudo determinar la ruta SharePoint para {descriptor.name}"
        )

    @traceable
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get the number of pages in a PDF."""
        try:
            with open(pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                return len(reader.pages)
        except Exception as e:
            self.logger.error(f"Error counting pages in {pdf_path}: {e}")
            return 0

    @traceable
    def split_pdf_into_chunks(self, pdf_path: str) -> list[str]:
        """Split PDF into chunks of max_pages and return temporary file paths."""
        temp_files = []
        try:
            with open(pdf_path, "rb") as pdf_file:
                reader = PdfReader(pdf_file)
                total_pages = len(reader.pages)

                for start_page in range(0, total_pages, self.max_pages_per_chunk):
                    end_page = min(start_page + self.max_pages_per_chunk, total_pages)

                    writer = PdfWriter()
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])

                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    with open(temp_file.name, "wb") as output_file:
                        writer.write(output_file)

                    temp_files.append(temp_file.name)
                    self.logger.info(
                        f"Created chunk {len(temp_files)}: pages {start_page+1}-{end_page}"
                    )

        except Exception as e:
            self.logger.error(f"Error splitting PDF {pdf_path}: {e}")
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
            return []

        return temp_files

    @traceable
    def encode_pdf(self, pdf_path: str) -> str:
        """Encode the pdf to base64."""
        try:
            with open(pdf_path, "rb") as pdf_file:
                return base64.b64encode(pdf_file.read()).decode("utf-8")
        except Exception as e:
            self.logger.error(f"Error encoding PDF {pdf_path}: {e}")
            return None

    @traceable
    def process_chunk(self, pdf_path: str, extraction_model: type[BaseModel]):
        """Process a single PDF chunk with Mistral OCR."""
        try:
            base64_pdf = self.encode_pdf(pdf_path)
            if not base64_pdf:
                return None

            request_params = {
                "model": "mistral-ocr-latest",
                "document": {
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{base64_pdf}",
                },
                "include_image_base64": False,
            }

            if extraction_model:
                try:
                    request_params["document_annotation_format"] = (
                        response_format_from_pydantic_model(extraction_model)
                    )
                except Exception as exc:
                    self.logger.warning(
                        "No se pudo generar schema pydantic para %s: %s", pdf_path, exc
                    )

            return self.client.ocr.process(**request_params)
        except Exception as e:
            self.logger.error(f"Error processing chunk {pdf_path}: {e}")
            return None

    @traceable
    def _resolve_pdf_path(self, pdf_path: str) -> tuple[str, list[str]]:
        """Ensure a local copy of the PDF and list temp paths for cleanup."""
        cleanup: list[str] = []
        try:
            parsed = urlparse(str(pdf_path))
        except Exception:
            parsed = None

        if parsed and parsed.scheme in {"http", "https"}:
            tmp_handle = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp_path = tmp_handle.name
            tmp_handle.close()
            try:
                with requests.get(pdf_path, stream=True, timeout=(10, 120)) as response:
                    response.raise_for_status()
                    with open(tmp_path, "wb") as fh:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                fh.write(chunk)
                cleanup.append(tmp_path)
                return tmp_path, cleanup
            except Exception as exc:
                self.logger.error(f"No se pudo descargar PDF {pdf_path}: {exc}")
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
                raise

        return pdf_path, cleanup

    def _get_sharepoint_client(self) -> SharePointClient:
        if self._sharepoint_client is None:
            tenant_id = os.getenv("TENANT_ID")
            client_id = os.getenv("CLIENT_ID")
            client_secret = os.getenv("CLIENT_SECRET")
            resource = os.getenv("RESOURCE") or "https://graph.microsoft.com"
            resource = resource.strip()
            if resource.endswith('/'):
                resource = resource[:-1]
            if not resource:
                resource = "https://graph.microsoft.com"
            if not (tenant_id and client_id and client_secret):
                raise RuntimeError(
                    "Credenciales de SharePoint no configuradas en el entorno (.env)"
                )
            self._sharepoint_client = SharePointClient(
                tenant_id, client_id, client_secret, resource
            )
        return self._sharepoint_client

    def _ensure_local_pdf(self, descriptor: FileDescriptor) -> tuple[str, list[str]]:
        cleanup: list[str] = []

        if descriptor.content_base64:
            suffix = os.path.splitext(descriptor.name or "")[1] or ".pdf"
            tmp_handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp_handle.close()
            try:
                decoded = base64.b64decode(descriptor.content_base64, validate=True)
            except Exception as exc:
                try:
                    os.unlink(tmp_handle.name)
                except Exception:
                    pass
                raise ValueError(
                    f"Contenido base64 invalido para {descriptor.name}: {exc}"
                ) from exc
            with open(tmp_handle.name, "wb") as fh:
                fh.write(decoded)
            cleanup.append(tmp_handle.name)
            return tmp_handle.name, cleanup

        if descriptor.source and descriptor.source.lower() == "sharepoint":
            client = self._get_sharepoint_client()
            reference = self._build_sharepoint_download_reference(descriptor, client)
            suffix = os.path.splitext(descriptor.name or "")[1] or ".pdf"
            tmp_handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            tmp_handle.close()
            target_dir = os.path.dirname(tmp_handle.name)
            target_name = os.path.basename(tmp_handle.name)
            try:
                client.download_file(reference, target_dir, target_name)
            except Exception:
                try:
                    os.unlink(tmp_handle.name)
                except Exception:
                    pass
                raise
            cleanup.append(tmp_handle.name)
            return tmp_handle.name, cleanup

        if descriptor.url:
            return self._resolve_pdf_path(descriptor.url)

        raise ValueError("Descriptor sin ubicacion accesible")

    def _process_document_sync(
        self, descriptor: FileDescriptor, extraction_model: type[BaseModel]
    ) -> list:
        label = descriptor.url or descriptor.name or "<sin nombre>"

        try:
            local_path, cleanup_paths = self._ensure_local_pdf(descriptor)
        except Exception as exc:
            self.logger.error(f"No se pudo preparar el PDF {label}: {exc}")
            return []

        results: list = []
        chunk_files: list[str] = []

        try:
            total_pages = self.get_pdf_page_count(local_path)
            self.logger.info(f"Processing PDF {label} with {total_pages} pages")

            if total_pages <= self.max_pages_per_chunk:
                result = self.process_chunk(local_path, extraction_model)
                if result:
                    results.append(result)
            else:
                chunk_files = self.split_pdf_into_chunks(local_path)
                for i, chunk_file in enumerate(chunk_files):
                    self.logger.info(f"Processing chunk {i+1}/{len(chunk_files)}")
                    result = self.process_chunk(chunk_file, extraction_model)
                    if result:
                        results.append(result)
        finally:
            for chunk_file in chunk_files:
                try:
                    os.unlink(chunk_file)
                except Exception as e:
                    self.logger.warning(
                        f"Could not delete temporary file {chunk_file}: {e}"
                    )
            for temp_path in cleanup_paths:
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    self.logger.warning(
                        f"Could not delete temporary file {temp_path}: {e}"
                    )

        return results

    async def process_document(
        self, descriptor: FileDescriptor, extraction_model: type[BaseModel]
    ) -> list:
        """Run blocking document processing in a worker thread."""
        return await asyncio.to_thread(
            self._process_document_sync, descriptor, extraction_model
        )

    def consolidate_chunks_data(
        self,
        chunk_responses: list,
        document_name: str,
        extraction_model: type[BaseModel],
    ):
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
                if hasattr(response, "document_annotation"):
                    annotation_data = response.document_annotation
                elif isinstance(response, dict) and "document_annotation" in response:
                    annotation_data = response["document_annotation"]

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
                        self.logger.warning(
                            f"Error parsing chunk {i+1} annotation: {e}"
                        )

            # Crear instancia del modelo Pydantic con los datos consolidados
            if all_chunk_data and extraction_model:
                try:
                    model_instance = extraction_model(**all_chunk_data)
                    self.logger.info(
                        f"Created {extraction_model.__name__} instance for {document_name}"
                    )
                    return model_instance
                except Exception as e:
                    self.logger.error(
                        f"Error creating model instance for {document_name}: {e}"
                    )
                    # Fallback: retornar los datos raw
                    return all_chunk_data

            self.logger.warning(
                f"No valid data to create model instance for {document_name}"
            )
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
                # Si son del mismo tipo pero no lista/dict, mantener el ÃƒÆ’Ã‚Âºltimo valor
                else:
                    target[key] = value
            else:
                target[key] = value

    @traceable
    async def run(
        self, state: IndexNodeState, config
    ) -> Command[Literal["op_reasoning_parallelization"]]:
        extraction_content = []

        raw_documents = state.get("documents", []) or []
        if not raw_documents:
            raw_documents = state.get("doc_path_list", []) or []

        documents: list[FileDescriptor] = []
        for value in raw_documents:
            descriptor = _coerce_to_descriptor(value)
            if descriptor is None:
                self.logger.warning(
                    "Descriptor de documento invalido ignorado: %s", value
                )
                continue
            documents.append(descriptor)

        extraction_model = state.get("data_extraction_model")

        for descriptor in documents:
            document_name = descriptor.name
            if not document_name:
                if descriptor.url:
                    document_name = os.path.basename(descriptor.url) or descriptor.url
                else:
                    document_name = "documento.pdf"

            chunk_responses = await self.process_document(descriptor, extraction_model)
            model_instance = await asyncio.to_thread(
                self.consolidate_chunks_data,
                chunk_responses,
                document_name,
                extraction_model,
            )

            extraction_content.append(
                IndexNodeOutput(
                    document_name=document_name, extracted_content=model_instance
                )
            )

            self.logger.info("Completed processing %s", document_name)

        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content=f"Procesados {len(extraction_content)} documentos."
                    )
                ],
                "extraction_content": [
                    NodeOutput(
                        set_name=state.get("set_name"),
                        extracted_content=extraction_content,
                    )
                ],
            },
            goto="op_reasoning_parallelization",
        )
