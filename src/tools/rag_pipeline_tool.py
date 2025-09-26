from __future__ import annotations
"""
RAG Pipeline Tool – Procesamiento de directorios/archivos (fix metadatas parquet)
---------------------------------------------------------------------------------
- Evita el error: "Cannot write struct type 'metadatas' with no child field to Parquet"
  añadiendo metadatos mínimos a cada chunk (source_dir, chunk_index).
- Resto: igual que versión anterior (OCR Mistral base64, Word/Excel loaders, etc.)

Requisitos:
- mistralai>=1.5.0 (MISTRAL_API_KEY)
- langchain, langchain_community, langchain_openai
- pandas, openpyxl, xlrd, scikit-learn, pyarrow
- PyPDF2 (para conteo de páginas)
- OPENAI_API_KEY
"""

import os
import base64
import json
import logging
import time
import uuid
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal, Type

import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_openai import OpenAIEmbeddings
from mistralai import Mistral
from mistralai.models import SDKError
from mistralai.extra import response_format_from_pydantic_model
from pydantic import BaseModel, Field

from src.config.template_config import TEMPLATE_SETS

from src.config.models.set_1 import Set1ExtractionModel
from src.config.models.set_2 import Set2ExtractionModel
from src.config.models.set_3 import Set3ExtractionModel
from src.config.models.set_4 import Set4ExtractionModel
from src.config.models.set_5 import Set5ExtractionModel
from src.config.models.set_6 import Set6ExtractionModel
from src.config.models.set_7 import Set7ExtractionModel
from src.config.models.set_8 import Set8ExtractionModel
from src.config.models.set_10 import Set10ExtractionModel
from src.config.models.set_11 import Set11ExtractionModel


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

SUPPORTED_EXTENSIONS: Dict[str, List[str]] = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx", ".xlsm"],
    "image": [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"],
}
ALL_EXTENSIONS: List[str] = [e for lst in SUPPORTED_EXTENSIONS.values() for e in lst]

SEP_DOCUMENT = ""
SEP_SHEET = "-----SHEET BREAK-----"
SEP_PAGE = "-----PAGE BREAK-----"

# Tipo alias para los modelos de validación
ValidationModelName = Literal[
    "Set1ExtractionModel", "Set2ExtractionModel", "Set3ExtractionModel", 
    "Set4ExtractionModel", "Set5ExtractionModel", "Set6ExtractionModel", 
    "Set7ExtractionModel", "Set8ExtractionModel", "Set10ExtractionModel", 
    "Set11ExtractionModel"
]


# =============================================================================
# MAPEO DE STRINGS A MODELOS PYDANTIC DE VALIDACIÓN
# =============================================================================

# Mapeo de strings a modelos Pydantic del sistema de validación
DOCUMENT_ANNOTATION_MODELS: Dict[str, Type[BaseModel]] = {
    "Set1ExtractionModel": Set1ExtractionModel,
    "Set2ExtractionModel": Set2ExtractionModel,
    "Set3ExtractionModel": Set3ExtractionModel,
    "Set4ExtractionModel": Set4ExtractionModel,
    "Set5ExtractionModel": Set5ExtractionModel,
    "Set6ExtractionModel": Set6ExtractionModel,
    "Set7ExtractionModel": Set7ExtractionModel,
    "Set8ExtractionModel": Set8ExtractionModel,
    "Set10ExtractionModel": Set10ExtractionModel,
    "Set11ExtractionModel": Set11ExtractionModel,
}

def get_document_annotation_model(model_name: Optional[ValidationModelName]) -> Optional[Type[BaseModel]]:
    """Obtener modelo Pydantic desde nombre exacto del modelo"""
    if not model_name:
        return None
    
    # Mapeo directo - el Literal ya garantiza que es un nombre válido
    # TODO Incorporar template sets para tener una versión generalizada de este agente
    # model = TEMPLATE_SETS[set_name]["data_extraction_model"]
    model = DOCUMENT_ANNOTATION_MODELS.get(model_name)
    if model:
        logger.info(f"[get_document_annotation_model] Usando modelo: {model.__name__}")
        return model
    
    # Esto no debería pasar con Literal, pero por seguridad
    logger.error(f"[get_document_annotation_model] Error interno: modelo '{model_name}' no encontrado en mapeo")
    return None


def _create_mistral_client() -> Mistral:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("Defina la variable MISTRAL_API_KEY con su API-Key de Mistral AI")
    return Mistral(api_key=api_key, timeout_ms=300000)


class RAGPipelineInput(BaseModel):
    directory: str = Field(..., description="Ruta a directorio o archivo local")
    chunk_size: int = Field(6000, description="Tamaño de chunk")
    chunk_overlap: int = Field(250, description="Overlap entre chunks")
    recursive: bool = Field(True, description="Buscar archivos en subdirectorios")
    specific_files: Optional[List[str]] = Field(
        None, description="Nombres de archivos específicos a procesar"
    )
    document_annotation_model: Optional[ValidationModelName] = Field(
        None, description="Modelo Pydantic para Document Annotations (estructura JSON de salida)"
    )


class DocumentExtractor:
    @staticmethod
    def _file_to_base64(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _extract_pdf_via_document_annotations(self, path_doc: str, document_annotation_format: Optional[Type[BaseModel]] = None, ocr_model: str = "mistral-ocr-latest", retries: int = 3) -> str:
        """Extrae PDF usando Document Annotations de Mistral con segmentación de num_batch_pages páginas"""
        client = _create_mistral_client()
        b64_pdf = self._file_to_base64(path_doc)
        
        # Obtener número total de páginas usando PyPDF como fallback
        total_pages = self._get_pdf_page_count(path_doc)
        logger.info(f"[Document Annotations] PDF tiene {total_pages} páginas: {path_doc}")
        
        # Segmentar en chunks de num_batch_pages páginas (límite de Document Annotations)
        page_chunks = []
        num_batch_pages = 7
        for start_page in range(0, total_pages, num_batch_pages):
            end_page = min(start_page + num_batch_pages, total_pages)
            page_range = list(range(start_page, end_page))
            page_chunks.append(page_range)
        
        logger.info(f"[Document Annotations] Procesando {len(page_chunks)} segmentos de páginas")
        
        all_results = []
        for chunk_idx, page_range in enumerate(page_chunks):
            logger.info(f"[Document Annotations] Procesando segmento {chunk_idx + 1}/{len(page_chunks)}: páginas {page_range[0]}-{page_range[-1]}")
            
            for attempt in range(1, retries + 1):
                try:
                    # Preparar parámetros para la llamada OCR
                    ocr_params = {
                        "model": ocr_model,
                        "pages": page_range,
                        "document": {
                            "type": "document_url",
                            "document_url": f"data:application/pdf;base64,{b64_pdf}"
                        },
                        "include_image_base64": False,
                    }
                    
                    # Agregar document_annotation_format si se proporciona
                    if document_annotation_format:
                        ocr_params["document_annotation_format"] = response_format_from_pydantic_model(document_annotation_format)
                    
                    ocr_response = client.ocr.process(**ocr_params)
                    
                    # Procesar respuesta
                    if document_annotation_format and hasattr(ocr_response, 'document_annotation') and ocr_response.document_annotation:
                        # Si hay document annotation, convertir JSON a string
                        json_content = ocr_response.document_annotation
                        if isinstance(json_content, str):
                            structured_content = json_content
                        else:
                            structured_content = json.dumps(json_content, ensure_ascii=False, indent=2)
                        
                        # También incluir el markdown de las páginas
                        #pages_markdown = [p.markdown for p in ocr_response.pages if p.markdown.strip()]
                        #markdown_content = f"\n{SEP_PAGE}\n".join(pages_markdown)
                        
                        # Combinar contenido estructurado
                        chunk_result = f"=== STRUCTURED ANNOTATION ===\n{structured_content}\n=== STRUCTURED ANNOTATION ==="
                    else:
                        # Fallback a markdown normal
                        pages_markdown = [p.markdown for p in ocr_response.pages if p.markdown.strip()]
                        chunk_result = f"\n{SEP_PAGE}\n".join(pages_markdown)
                    
                    if chunk_result.strip():
                        all_results.append(chunk_result)
                        logger.info(f"[Document Annotations] Segmento {chunk_idx + 1} extraído: {len(chunk_result)} chars")
                    break
                    
                except SDKError as e:
                    if attempt == retries or getattr(e, "status_code", 0) < 500:
                        logger.error(f"[Document Annotations] Error SDK en segmento {chunk_idx + 1}, intento {attempt}: {e}")
                        if attempt == retries:
                            # Fallback a OCR básico para este segmento
                            fallback_result = self._extract_pdf_segment_basic_ocr(path_doc, page_range, ocr_model)
                            if fallback_result.strip():
                                all_results.append(fallback_result)
                        continue
                    time.sleep(2 ** (attempt - 1))
                except Exception as e:
                    logger.warning(f"[Document Annotations] Error en segmento {chunk_idx + 1}, intento {attempt}: {e}")
                    if attempt == retries:
                        # Fallback a OCR básico para este segmento
                        fallback_result = self._extract_pdf_segment_basic_ocr(path_doc, page_range, ocr_model)
                        if fallback_result.strip():
                            all_results.append(fallback_result)
                    else:
                        time.sleep(2 ** (attempt - 1))
        
        final_result = f"\n{SEP_DOCUMENT}\n".join(all_results)
        logger.info(f"[Document Annotations] PDF completo extraído: {len(final_result)} chars")
        return final_result
    
    def _get_pdf_page_count(self, path_doc: str) -> int:
        """Obtiene el número de páginas del PDF usando PyPDF"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path_doc)
            return len(reader.pages)
        except Exception:
            try:
                # Fallback usando PyPDFLoader de langchain
                pages = PyPDFLoader(path_doc).load()
                return len(pages)
            except Exception as e:
                logger.warning(f"[_get_pdf_page_count] No se pudo determinar páginas de {path_doc}: {e}")
                return 50  # Valor por defecto conservador
    
    def _extract_pdf_segment_basic_ocr(self, path_doc: str, page_range: List[int], ocr_model: str) -> str:
        """Fallback para extraer un segmento de PDF usando OCR básico"""
        try:
            client = _create_mistral_client()
            b64_pdf = self._file_to_base64(path_doc)
            
            ocr_response = client.ocr.process(
                model=ocr_model,
                pages=page_range,
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{b64_pdf}"
                },
                include_image_base64=False,
            )
            
            pages_markdown = [p.markdown for p in ocr_response.pages if p.markdown.strip()]
            return f"\n{SEP_PAGE}\n".join(pages_markdown)
        except Exception as e:
            logger.error(f"[_extract_pdf_segment_basic_ocr] Error en páginas {page_range}: {e}")
            return ""

    def extract_pdf(self, path_doc: str, document_annotation_format: Optional[Type[BaseModel]] = None) -> str:
        try:
            logger.info(f"[PDF] Intentando PyPDF: {path_doc}")
            pages = PyPDFLoader(path_doc).load()
            text = f"\n{SEP_PAGE}\n".join(p.page_content for p in pages if p.page_content.strip())
            if text.strip():
                return text
            logger.warning(f"[PDF] PyPDF no extrajo texto útil: {path_doc}")
        except Exception as e:
            logger.warning(f"[PDF] PyPDF falló para {path_doc}: {e}")

        logger.info(f"[PDF] Intentando Document Annotations Mistral: {path_doc}")
        return self._extract_pdf_via_document_annotations(path_doc, document_annotation_format)

    def extract_image(self, path_doc: str, ocr_model: str = "mistral-ocr-latest", retries: int = 3) -> str:
        client = _create_mistral_client()
        b64_image = self._file_to_base64(path_doc)
        
        # Detectar el tipo MIME de la imagen
        ext = Path(path_doc).suffix.lower()
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg', 
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')

        for attempt in range(1, retries + 1):
            try:
                ocr_response = client.ocr.process(
                    model=ocr_model,
                    document={
                        "type": "image_url",
                        "image_url": f"data:{mime_type};base64,{b64_image}"
                    },
                    include_image_base64=False,
                )
                pages_markdown: List[str] = [p.markdown for p in ocr_response.pages]
                return f"\n{SEP_PAGE}\n".join(pages_markdown)
            except SDKError as e:
                if attempt == retries or getattr(e, "status_code", 0) < 500:
                    raise
                time.sleep(2 ** (attempt - 1))
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(2 ** (attempt - 1))
        return ""

    def extract_word(self, path_doc: str) -> str:
        ext = Path(path_doc).suffix.lower()
        if ext == ".docx":
            try:
                loader = Docx2txtLoader(path_doc)
                docs = loader.load()
                content = "\n".join(doc.page_content for doc in docs if doc.page_content.strip())
                if content.strip():
                    return content
            except Exception as e:
                logger.warning(f"[WORD] Docx2txt falló para {path_doc}: {e}")
        docs = UnstructuredWordDocumentLoader(path_doc).load()
        return "\n".join(doc.page_content for doc in docs if doc.page_content.strip())

    def extract_excel(self, path_doc: str) -> str:
        ext = Path(path_doc).suffix.lower()
        if ext not in (".xls", ".xlsx", ".xlsm"):
            raise ValueError(f"{path_doc} no es un Excel soportado.")

        engine = "xlrd" if ext == ".xls" else "openpyxl"
        try:
            xls = pd.ExcelFile(path_doc, engine=engine)
        except Exception as e:
            raise ValueError(f"No se pudo abrir {path_doc}: {e}") from e

        sheets: List[str] = []
        for name in xls.sheet_names:
            df = xls.parse(name)
            csv_content = df.to_csv(sep="\t", index=False)
            sheets.append(f"--SHEET:{name}--\n{csv_content}")

        if not sheets:
            raise ValueError(f"No se pudo extraer contenido de {path_doc}")
        return f"\n{SEP_SHEET}\n".join(sheets)

    def extract_single_document(self, path_doc: str, document_annotation_format: Optional[Type[BaseModel]] = None) -> str:
        ext = Path(path_doc).suffix.lower()
        try:
            if ext in SUPPORTED_EXTENSIONS["pdf"]:
                return self.extract_pdf(path_doc, document_annotation_format)
            if ext in SUPPORTED_EXTENSIONS["word"]:
                return self.extract_word(path_doc)
            if ext in SUPPORTED_EXTENSIONS["excel"]:
                return self.extract_excel(path_doc)
            if ext in SUPPORTED_EXTENSIONS["image"]:
                return self.extract_image(path_doc)
            raise ValueError(f"Extensión no soportada: {ext}")
        except Exception as e:
            logger.error(f"[Extractor] Error procesando {path_doc}: {e}")
            raise


class RAGProcessor:
    def __init__(self, chunk_size: int = 6000, chunk_overlap: int = 250, document_annotation_format: Optional[Type[BaseModel]] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.document_annotation_format = document_annotation_format
        self.extractor = DocumentExtractor()

    def discover_files(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> List[str]:
        if specific_files:
            out: List[str] = []
            for f in specific_files:
                p = Path(f)
                p = p if p.is_absolute() else Path(directory) / p
                if p.exists() and p.is_file() and p.suffix.lower() in ALL_EXTENSIONS:
                    try:
                        _ = p.stat().st_size
                        out.append(str(p))
                    except Exception as e:
                        logger.warning(f"[discover_files] No accesible: {p} - {e}")
            return out

        dpath = Path(directory)
        if not dpath.is_dir():
            raise ValueError(f"La ruta {directory} no es un directorio válido")

        pattern = "**/*" if recursive else "*"
        files: List[str] = []
        for fp in dpath.glob(pattern):
            if fp.is_file() and fp.suffix.lower() in ALL_EXTENSIONS:
                try:
                    _ = fp.stat().st_size
                    files.append(str(fp))
                except Exception:
                    logger.warning(f"[discover_files] No accesible: {fp}")

        if files:
            cnt = Counter(Path(f).suffix.lower() for f in files)
            logger.info(f"[discover_files] {len(files)} archivos en {directory}: {dict(cnt)}")
        else:
            logger.warning(f"[discover_files] No se encontraron archivos soportados en {directory}")
        return files

    def extract_directory_content(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> tuple[str, List[str]]:
        files = self.discover_files(directory, recursive, specific_files)
        if not files:
            logger.warning(f"[extract_directory_content] Sin archivos en {directory}")
            return "", []

        logger.info(
            f"[extract_directory_content] Procesando {len(files)} archivo(s) "
            + ("específicos" if specific_files else "descubiertos")
            + f" en {directory}"
        )

        contents: List[str] = []
        processed_files: List[str] = []
        for fp in files:
            content = self.extractor.extract_single_document(fp, self.document_annotation_format)
            if content.strip():
                contents.append(content)
                processed_files.append(fp)
        return f"\n{SEP_DOCUMENT}\n".join(contents), processed_files

    def _create_json_aware_splitter(self) -> RecursiveCharacterTextSplitter:
        """Crea un splitter que considera la estructura JSON para chunking inteligente"""
        # Separadores optimizados para contenido JSON y estructurado
        json_separators = [
            SEP_DOCUMENT,
            SEP_SHEET,
            SEP_PAGE,
            "\n\n",
            "\n}",  # Final de objetos JSON
            "},",   # Separación entre objetos JSON
            "\n]",  # Final de arrays JSON
            "],",   # Separación entre arrays JSON
            "\n",
            " ",
            ""
        ]
        
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=json_separators,
        )
    
    def split_documents(self, content: str, directory: str, processed_files: Optional[List[str]] = None) -> List[Document]:
        if not content.strip():
            return []

        # Usar splitter optimizado para JSON si hay contenido estructurado
        if "=== STRUCTURED ANNOTATION ===" in content:
            logger.info("[split_documents] Detectado contenido estructurado, usando chunking JSON-aware")
            splitter = self._create_json_aware_splitter()
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=[SEP_DOCUMENT, SEP_SHEET, SEP_PAGE, "\n\n", "\n"],
            )

        # Metadatos base para evitar struct vacío en parquet
        base_md = {"source_dir": directory}
        doc = Document(page_content=content, metadata=base_md)
        chunks = splitter.split_documents([doc])

        # Crear mapeo de archivos procesados para asignar source_dir correcto
        file_mapping = {}
        if processed_files:
            # Dividir el contenido por SEP_DOCUMENT para mapear chunks a archivos
            content_parts = content.split(f"\n{SEP_DOCUMENT}\n")
            for i, file_path in enumerate(processed_files):
                if i < len(content_parts):
                    # Crear source_dir con directorio + nombre de archivo (sin extensión)
                    file_name = Path(file_path).stem  # nombre sin extensión
                    source_dir_with_file = os.path.join(directory, file_name)
                    file_mapping[i] = source_dir_with_file

        # Garantizar que cada chunk tenga AL MENOS una clave en metadata
        fixed: List[Document] = []
        for i, c in enumerate(chunks):
            md = dict(c.metadata or {})
            
            # Determinar qué archivo corresponde a este chunk
            chunk_source_dir = directory  # valor por defecto
            source_file_name = ""  # nombre del archivo para incluir en el contenido
            
            if file_mapping:
                # Buscar en qué parte del contenido está este chunk
                chunk_content = c.page_content
                for file_idx, source_dir_with_file in file_mapping.items():
                    if file_idx < len(processed_files):
                        # Si el chunk contiene contenido del archivo, usar su source_dir
                        content_parts = content.split(f"\n{SEP_DOCUMENT}\n")
                        if file_idx < len(content_parts) and content_parts[file_idx] in content:
                            # Verificar si el chunk pertenece a este archivo
                            if any(part.strip() in chunk_content for part in content_parts[file_idx].split("\n") if part.strip()):
                                chunk_source_dir = source_dir_with_file
                                source_file_name = source_dir_with_file
                                break
            
            # Si no se encontró mapeo específico, usar directorio base
            if not source_file_name:
                source_file_name = directory
            
            # Agregar el nombre completo al contenido del chunk
            enhanced_content = f"[SOURCE: {source_file_name}]\n\n{c.page_content}"
            c.page_content = enhanced_content
            
            md.setdefault("source_dir", chunk_source_dir)
            md.setdefault("chunk_index", i)
            # Marcar si el chunk contiene contenido estructurado
            if "=== STRUCTURED ANNOTATION ===" in c.page_content:
                md["content_type"] = "structured_annotation"
            elif "=== MARKDOWN CONTENT ===" in c.page_content:
                md["content_type"] = "markdown_content"
            else:
                md["content_type"] = "standard"
            c.metadata = md
            fixed.append(c)

        return [c for c in fixed if c.page_content.strip()]

    def _safe_build_vectorstore(
        self, splits: List[Document], embeddings: OpenAIEmbeddings, persist_path: Path
    ) -> SKLearnVectorStore:
        try:
            return SKLearnVectorStore.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_path=persist_path.as_posix(),
                serializer="parquet",
            )
        except Exception as e:
            msg = str(e).lower()
            tokenish = any(
                s in msg
                for s in (
                    "max_tokens_per_request",
                    "maximum context length",
                    "too many inputs",
                    "invalidrequesterror",
                )
            )
            if not tokenish:
                raise
            logger.warning("[_safe_build_vectorstore] Exceso de tokens/inputs → reintento con chunk_size=32")
            smaller = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=32)
            return SKLearnVectorStore.from_documents(
                documents=splits,
                embedding=smaller,
                persist_path=persist_path.as_posix(),
                serializer="parquet",
            )

    # ⬇️ FIX adicional (cinturón y tirantes): sanitizar metadatos antes de persistir
    def _ensure_metadata(self, splits: List[Document], directory: str) -> List[Document]:
        for i, d in enumerate(splits):
            if not d.metadata:
                d.metadata = {"source_dir": directory, "chunk_index": i}
            else:
                d.metadata.setdefault("source_dir", directory)
                d.metadata.setdefault("chunk_index", i)
        return splits

    def create_vectorstore_from_splits(self, splits: List[Document], directory: str) -> str:
        if not splits:
            raise RuntimeError(f"Sin contenido utilizable para {directory}: no se creará vectorstore")

        # ⬇️ asegurar metadatos válidos
        splits = self._ensure_metadata(splits, directory)

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        output_dir = (Path(__file__).resolve().parents[2] / "vectorstores").resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        dir_name = Path(directory).name
        unique_id = str(uuid.uuid4())[:8]
        output_path = output_dir / f"vectorstore_{dir_name}_{unique_id}.parquet"

        vs = self._safe_build_vectorstore(splits, embeddings, output_path)
        vs.persist()
        return str(output_path)

    def process_directory(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            content, processed_files = self.extract_directory_content(directory, recursive, specific_files)
            splits = self.split_documents(content, directory, processed_files)
            vectorstore_path = self.create_vectorstore_from_splits(splits, directory)
            
            # Estadísticas adicionales sobre el contenido procesado
            content_stats = {
                "total_chunks": len(splits),
                "structured_chunks": len([c for c in splits if c.metadata.get("content_type") == "structured_annotation"]),
                "markdown_chunks": len([c for c in splits if c.metadata.get("content_type") == "markdown_content"]),
                "standard_chunks": len([c for c in splits if c.metadata.get("content_type") == "standard"]),
                "has_document_annotations": self.document_annotation_format is not None
            }
            
            return {
                "directory": directory,
                "vectorstore_path": vectorstore_path,
                "chunks_count": len(splits),
                "content_stats": content_stats,
                "status": "success",
            }
        except Exception as e:
            logger.error(f"[process_directory] Error en {directory}: {e}")
            return {
                "directory": directory,
                "vectorstore_path": None,
                "error": str(e),
                "status": "failed",
            }


class RAGPipelineTool(BaseTool):
    name: str = "rag_pipeline_tool"
    description: str = (
        "Procesa un directorio o archivo (PDF/Word/Excel/Imágenes) usando Document Annotations de Mistral "
        "para extracción estructurada, chunk-ea con soporte JSON-aware, vectoriza y genera un "
        "vectorstore persistente (.parquet). Soporta modelos Pydantic para anotaciones estructuradas. Devuelve JSON."
    )
    args_schema: Type[BaseModel] = RAGPipelineInput
    return_direct: bool = False
    handle_tool_error: bool = True

    def _run(
        self,
        directory: str,
        chunk_size: int = 6000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        document_annotation_model: Optional[ValidationModelName] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        if not directory:
            raise ToolException("Se requiere una ruta (directorio o archivo) para procesar")

        p = Path(directory)
        if not p.exists():
            return json.dumps(
                {
                    "directory": directory,
                    "vectorstore_path": None,
                    "chunks_count": 0,
                    "status": "failed",
                    "error": f"La ruta no existe: {directory}",
                },
                indent=2,
                ensure_ascii=False,
            )

        if p.is_file():
            work_directory = str(p.parent)
            if specific_files is None:
                specific_files = [p.name]
            else:
                specific_files = list(specific_files) + [p.name]
        else:
            work_directory = directory

        # Convertir string a modelo Pydantic
        document_annotation_format = get_document_annotation_model(document_annotation_model)
        
        processor = RAGProcessor(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            document_annotation_format=document_annotation_format
        )

        try:
            logger.info(f"[RAGPipelineTool] Procesando: {work_directory}")
            result = processor.process_directory(
                directory=work_directory, recursive=recursive, specific_files=specific_files
            )
            if result["status"] == "success":
                logger.info(f"✓ {work_directory} → {result['vectorstore_path']} ({result['chunks_count']} chunks)")
            else:
                logger.error(f"✗ {work_directory} → {result.get('error', 'Unknown error')}")
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"[RAGPipelineTool] Error crítico en {work_directory}: {exc}")
            return json.dumps(
                {
                    "directory": work_directory,
                    "vectorstore_path": None,
                    "chunks_count": 0,
                    "status": "failed",
                    "error": str(exc),
                },
                indent=2,
                ensure_ascii=False,
            )

    async def _arun(
        self,
        directory: str,
        chunk_size: int = 6000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        document_annotation_model: Optional[ValidationModelName] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        import asyncio

        return await asyncio.to_thread(
            self._run,
            directory,
            chunk_size,
            chunk_overlap,
            recursive,
            specific_files,
            document_annotation_model,
            run_manager.get_sync() if run_manager else None,
        )
