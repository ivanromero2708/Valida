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
- OPENAI_API_KEY
"""
import os
import base64
import json
import logging
import time
import uuid
import io
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Literal, Tuple
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
from pydantic import BaseModel, Field
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
SUPPORTED_EXTENSIONS: Dict[str, List[str]] = {
    "pdf": [".pdf"],
    "word": [".doc", ".docx"],
    "excel": [".xls", ".xlsx", ".xlsm"],
    "image": [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"],
}
ALL_EXTENSIONS: List[str] = [e for lst in SUPPORTED_EXTENSIONS.values() for e in lst]
SEP_DOCUMENT = "=====DOCUMENT BREAK====="
SEP_SHEET = "-----SHEET BREAK-----"
SEP_PAGE = "-----PAGE BREAK-----"

ANNOTATION_MAX_ATTEMPTS = 3
ANNOTATION_BACKOFF_SECONDS = 1.5

try:
    from mistralai.extra import response_format_from_pydantic_model  # type: ignore
except Exception:  # pragma: no cover
    response_format_from_pydantic_model = None


try:
    from pdf2image import convert_from_path  # type: ignore
except Exception:  # pragma: no cover
    convert_from_path = None


@dataclass
class PageOCR:
    index: int
    markdown: str
    image_b64: Optional[str] = None


def _parse_md_tables(md: str) -> List[List[List[str]]]:
    tables: List[List[List[str]]] = []
    current: List[List[str]] = []
    for raw_line in md.splitlines():
        line = raw_line.strip()
        if line.startswith('|'):
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            current.append(cells)
        else:
            if current:
                tables.append(current)
                current = []
    if current:
        tables.append(current)
    return tables


def _table_tis(table: List[List[str]]) -> float:
    if not table or len(table) < 2:
        return 0.0
    col_counts = [len(row) for row in table]
    if not col_counts:
        return 0.0
    target_cols = max(set(col_counts), key=col_counts.count)
    total_rows = len(col_counts)
    col_var_penalty = sum(1 for count in col_counts if count != target_cols) / max(1, total_rows)

    def classify(cell: str) -> str:
        cell = cell.strip()
        if not cell:
            return 'empty'
        if re.fullmatch(r"[-+]?\d+(?:[.,]\d+)?\s*%?", cell):
            return 'num'
        if re.fullmatch(r"[A-Za-z]{1,4}\d{2,}[-/A-Za-z0-9]*", cell):
            return 'id'
        return 'text'

    aligned_rows = [row for row in table if len(row) == target_cols]
    if not aligned_rows:
        return 0.0
    classified = [[classify(cell) for cell in row] for row in aligned_rows]
    columns = list(zip(*classified))
    type_penalty = 0.0
    for col in columns:
        freq: Dict[str, int] = {}
        for typ in col:
            freq[typ] = freq.get(typ, 0) + 1
        type_penalty += 1 - (max(freq.values()) / len(col))
    type_penalty /= max(1, len(columns))
    empty_penalty = sum(1 for col in columns if sum(1 for typ in col if typ == 'empty') / len(col) > 0.4)
    empty_penalty /= max(1, len(columns))
    score = 1.0 - (0.5 * col_var_penalty + 0.35 * type_penalty + 0.15 * empty_penalty)
    return max(0.0, min(1.0, score))


def page_tis(markdown: str) -> Tuple[float, int]:
    tables = _parse_md_tables(markdown)
    if not tables:
        return 1.0, 0
    scores = [_table_tis(table) for table in tables]
    return min(scores), len(tables)


def _repair_table_block(lines: List[str]) -> List[str]:
    rows = [[cell.strip() for cell in line.strip().strip('|').split('|')] for line in lines]
    if not rows:
        return lines
    counts = [len(row) for row in rows]
    target_cols = max(set(counts), key=counts.count)
    patterns = [
        re.compile(r"^(.*?)(\d{2,3}[.,]\d+\s*%.*)$"),
        re.compile(r"^(.*?)([A-Z]{1,4}\d{2,}[-/A-Za-z0-9].*)$"),
    ]
    fixed: List[List[str]] = []
    for row in rows:
        if len(row) == target_cols - 1:
            idx_long = max(range(len(row)), key=lambda pos: len(row[pos]))
            candidate = row[idx_long]
            repaired = False
            for pattern in patterns:
                match = pattern.match(candidate)
                if match:
                    left, right = match.group(1).strip(), match.group(2).strip()
                    rebuilt = row[:idx_long] + [left, right] + row[idx_long + 1 :]
                    if len(rebuilt) == target_cols:
                        fixed.append(rebuilt)
                        repaired = True
                        break
            if not repaired:
                fixed.append(row)
        else:
            fixed.append(row)
    return ['| ' + ' | '.join(row) + ' |' for row in fixed]


def try_repair_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    if not lines:
        return markdown
    output: List[str] = []
    buffer: List[str] = []
    for line in lines:
        if line.strip().startswith('|'):
            buffer.append(line)
            continue
        if buffer:
            output.extend(_repair_table_block(buffer))
            buffer = []
        output.append(line)
    if buffer:
        output.extend(_repair_table_block(buffer))
    return "\n".join(output)


@dataclass
class FallbackPolicy:
    enable_repair: bool = True
    enable_annotation: bool = True
    enable_raster: bool = False
    suspect_threshold: float = 0.7
    max_retry_pages: int = 4
    annotation_schema_name: Optional[str] = None


class GenericTable(BaseModel):
    rows: List[List[str]]


def _get_mistral_client(api_key: Optional[str] = None) -> Mistral:
    if api_key:
        return Mistral(api_key=api_key, timeout_ms=300000)
    return _create_mistral_client()


def _resolve_annotation_model(schema_name: Optional[str]) -> Type[BaseModel]:
    if not schema_name or schema_name.lower() in {'generic_table', 'generic', 'default'}:
        return GenericTable
    logger.warning(f"[annotation] Esquema no reconocido '{schema_name}', se usa GenericTable")
    return GenericTable


def annotate_page_as_table_json(
    b64_pdf: str,
    page_index: int,
    policy: FallbackPolicy,
    api_key: Optional[str] = None,
) -> Optional[List[List[str]]]:
    if response_format_from_pydantic_model is None:
        logger.debug("[annotation] response_format_from_pydantic_model no disponible")
        return None
    schema_model = _resolve_annotation_model(policy.annotation_schema_name)
    fmt = response_format_from_pydantic_model(schema_model)
    last_error: Optional[Exception] = None
    for attempt in range(1, ANNOTATION_MAX_ATTEMPTS + 1):
        try:
            client = _get_mistral_client(api_key)
            response = client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": f"data:application/pdf;base64,{b64_pdf}"
                },
                pages=[page_index],
                document_annotation_format=fmt,
                include_image_base64=False,
            )
            annotation = getattr(response, "document_annotation", None)
            if not annotation:
                return None
            if isinstance(annotation, dict):
                rows = annotation.get("rows")
            else:
                rows = getattr(annotation, "rows", None)
            if rows and isinstance(rows, list) and isinstance(rows[0], list):
                return rows
            return None
        except Exception as exc:
            last_error = exc
            if attempt == ANNOTATION_MAX_ATTEMPTS:
                logger.warning(f"[annotation] Fallo Mistral annotation pagina {page_index}: {exc}")
                break
            sleep_for = ANNOTATION_BACKOFF_SECONDS * attempt
            logger.warning(
                f"[annotation] Reintentando annotation pagina {page_index} (intento {attempt}/{ANNOTATION_MAX_ATTEMPTS}) tras error: {exc}"
            )
            time.sleep(sleep_for)
    if last_error:
        logger.debug(f"[annotation] Ultimo error annotation pagina {page_index}: {last_error}")
    return None


def rasterize_and_annotate(
    pdf_path: str,
    page_index: int,
    policy: FallbackPolicy,
    api_key: Optional[str] = None,
) -> Optional[List[List[str]]]:
    if convert_from_path is None:
        logger.debug('[raster] pdf2image no disponible, se omite rasterizado')
        return None
    try:
        images = convert_from_path(
            pdf_path,
            dpi=320,
            first_page=page_index + 1,
            last_page=page_index + 1,
        )
    except Exception as exc:
        logger.warning(f"[raster] Fallo rasterizado pagina {page_index}: {exc}")
        return None
    if not images:
        return None
    buf = io.BytesIO()
    images[0].save(buf, format='PNG')
    b64_png = base64.b64encode(buf.getvalue()).decode()
    if response_format_from_pydantic_model is None:
        return None
    schema_model = _resolve_annotation_model(policy.annotation_schema_name)
    fmt = response_format_from_pydantic_model(schema_model)
    last_error: Optional[Exception] = None
    for attempt in range(1, ANNOTATION_MAX_ATTEMPTS + 1):
        try:
            client = _get_mistral_client(api_key)
            response = client.ocr.process(
                model='mistral-ocr-latest',
                document={
                    'type': 'image_url',
                    'image_url': f"data:image/png;base64,{b64_png}"
                },
                document_annotation_format=fmt,
                include_image_base64=False,
            )
            annotation = getattr(response, 'document_annotation', None)
            if isinstance(annotation, dict):
                rows = annotation.get('rows')
            else:
                rows = getattr(annotation, 'rows', None)
            if rows and isinstance(rows, list) and isinstance(rows[0], list):
                return rows
            return None
        except Exception as exc:
            last_error = exc
            if attempt == ANNOTATION_MAX_ATTEMPTS:
                logger.warning(f"[raster] Fallo annotation desde imagen: {exc}")
                break
            sleep_for = ANNOTATION_BACKOFF_SECONDS * attempt
            logger.warning(
                f"[raster] Reintentando annotation desde imagen pagina {page_index} (intento {attempt}/{ANNOTATION_MAX_ATTEMPTS}) tras error: {exc}"
            )
            time.sleep(sleep_for)
    if last_error:
        logger.debug(f"[raster] Ultimo error annotation imagen pagina {page_index}: {last_error}")
    return None


def ocr_pdf_pages_with_images(pdf_path: str) -> Tuple[List[PageOCR], str]:
    with open(pdf_path, 'rb') as handle:
        b64_pdf = base64.b64encode(handle.read()).decode()
    client = _get_mistral_client()
    response = client.ocr.process(
        model='mistral-ocr-latest',
        document={
            'type': 'document_url',
            'document_url': f"data:application/pdf;base64,{b64_pdf}"
        },
        include_image_base64=True,
    )
    pages: List[PageOCR] = []
    for idx, page in enumerate(response.pages):
        pages.append(
            PageOCR(
                index=getattr(page, 'index', idx),
                markdown=getattr(page, 'markdown', '') or '',
                image_b64=getattr(page, 'image_base64', None),
            )
        )
    return pages, b64_pdf


def normalize_pages_to_documents(
    directory: str,
    source_file: str,
    pages: List[PageOCR],
    policy: FallbackPolicy,
    b64_pdf: str,
) -> List[Document]:
    documents: List[Document] = []
    retries = 0
    for page in pages:
        tis, _ = page_tis(page.markdown)
        suspect = tis < policy.suspect_threshold
        content = page.markdown
        origin = 'markdown'
        if suspect and policy.enable_repair:
            repaired = try_repair_markdown(content)
            new_tis, _ = page_tis(repaired)
            if new_tis > tis:
                content = repaired
                tis = new_tis
                suspect = tis < policy.suspect_threshold
                origin = 'markdown+repair'
        if suspect and policy.enable_annotation and retries < policy.max_retry_pages:
            rows = annotate_page_as_table_json(b64_pdf, page.index, policy)
            if rows:
                content = "\n".join("	".join(cell or '' for cell in row) for row in rows)
                tis = 1.0
                suspect = False
                origin = 'annotation'
                retries += 1
        if suspect and policy.enable_raster and retries < policy.max_retry_pages:
            rows = rasterize_and_annotate(source_file, page.index, policy)
            if rows:
                content = "\n".join("	".join(cell or '' for cell in row) for row in rows)
                tis = 1.0
                suspect = False
                origin = 'raster+annotation'
                retries += 1
        doc_metadata = {
            'source_dir': directory,
            'source_file': source_file,
            'page_num': page.index + 1,
            'image_b64': page.image_b64,
            'tis': round(tis, 3),
            'suspect': suspect,
            'extraction_kind': origin,
        }
        documents.append(Document(page_content=content, metadata=doc_metadata))
    for idx, document in enumerate(documents):
        document.metadata.setdefault('chunk_index', idx)
    return documents


def process_pdf_with_qc(
    directory: str,
    pdf_path: str,
    policy: FallbackPolicy,
) -> List[Document]:
    pages, b64_pdf = ocr_pdf_pages_with_images(pdf_path)
    return normalize_pages_to_documents(
        directory=directory,
        source_file=pdf_path,
        pages=pages,
        policy=policy,
        b64_pdf=b64_pdf,
    )
def _create_mistral_client() -> Mistral:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError("Defina la variable MISTRAL_API_KEY con su API-Key de Mistral AI")
    return Mistral(api_key=api_key, timeout_ms=300000)
class RAGPipelineInput(BaseModel):
    directory: str = Field(..., description="Ruta a directorio o archivo local")
    chunk_size: int = Field(2000, description="Tamaño de chunk")
    chunk_overlap: int = Field(250, description="Overlap entre chunks")
    recursive: bool = Field(True, description="Buscar archivos en subdirectorios")
    specific_files: Optional[List[str]] = Field(
        None, description="Nombres de archivos específicos a procesar"
    )
    table_qc: bool = Field(True, description="Activa el control de calidad estructural para tablas OCR")
    fallback_policy: Literal["none", "repair", "annotation", "raster", "auto"] = Field("auto", description="Escalado de fallbacks cuando una pagina luce corrupta")
    suspect_threshold: float = Field(0.7, description="Umbral minimo del Table Integrity Score (0-1)")
    max_retry_pages: int = Field(4, description="Reintentos maximos de anotacion/raster segun fallback")
    annotation_schema_name: Optional[str] = Field(None, description="Esquema de Document Annotation a usar, si aplica")
class DocumentExtractor:
    @staticmethod
    def _file_to_base64(path: str) -> str:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    def _extract_pdf_via_mistral_ocr(self, path_doc: str, ocr_model: str = "mistral-ocr-latest", retries: int = 3) -> str:
        client = _create_mistral_client()
        b64_pdf = self._file_to_base64(path_doc)
        for attempt in range(1, retries + 1):
            try:
                ocr_response = client.ocr.process(
                    model=ocr_model,
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{b64_pdf}"
                    },
                    include_image_base64=False,
                )
                pages_markdown: List[str] = [p.markdown for p in ocr_response.pages]
                result = f"\n{SEP_PAGE}\n".join(pages_markdown)
                if result.strip():
                    logger.info(f"[OCR Mistral] PDF extraído: {len(result)} chars")
                return result
            except SDKError as e:
                if attempt == retries or getattr(e, "status_code", 0) < 500:
                    raise
                time.sleep(2 ** (attempt - 1))
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(2 ** (attempt - 1))
        return ""
    def extract_pdf(self, path_doc: str) -> str:
        try:
            logger.info(f"[PDF] Intentando PyPDF: {path_doc}")
            pages = PyPDFLoader(path_doc).load()
            text = f"\n{SEP_PAGE}\n".join(p.page_content for p in pages if p.page_content.strip())
            if text.strip():
                return text
            logger.warning(f"[PDF] PyPDF no extrajo texto útil: {path_doc}")
        except Exception as e:
            logger.warning(f"[PDF] PyPDF falló para {path_doc}: {e}")
        logger.info(f"[PDF] Intentando OCR Mistral: {path_doc}")
        return self._extract_pdf_via_mistral_ocr(path_doc)
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
                content = "\n".join("	".join(cell or "" for cell in row) for row in rows)
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
    def extract_single_document(self, path_doc: str) -> str:
        ext = Path(path_doc).suffix.lower()
        try:
            if ext in SUPPORTED_EXTENSIONS["pdf"]:
                return self.extract_pdf(path_doc)
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
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 250, table_qc: bool = True, fallback_policy: Literal["none", "repair", "annotation", "raster", "auto"] = "auto", suspect_threshold: float = 0.7, max_retry_pages: int = 4, annotation_schema_name: Optional[str] = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.table_qc = table_qc
        self.fallback_policy_mode = fallback_policy
        self.suspect_threshold = suspect_threshold
        self.max_retry_pages = max_retry_pages
        self.annotation_schema_name = annotation_schema_name
        self.extractor = DocumentExtractor()
    def _build_fallback_policy(self) -> FallbackPolicy:
        mode = (self.fallback_policy_mode or "auto").lower()
        valid_modes = {"none", "repair", "annotation", "raster", "auto"}
        if mode not in valid_modes:
            logger.warning(f"[RAGProcessor] fallback_policy desconocido '{mode}', se usa 'auto'")
            mode = "auto"
        enable_repair = mode in {"repair", "annotation", "raster", "auto"}
        enable_annotation = mode in {"annotation", "raster", "auto"}
        enable_raster = mode in {"raster", "auto"}
        if mode == "none":
            enable_repair = False
            enable_annotation = False
            enable_raster = False
        return FallbackPolicy(
            enable_repair=enable_repair,
            enable_annotation=enable_annotation,
            enable_raster=enable_raster,
            suspect_threshold=self.suspect_threshold,
            max_retry_pages=self.max_retry_pages,
            annotation_schema_name=self.annotation_schema_name,
        )
    def extract_documents_with_qc(
        self,
        directory: str,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
    ) -> List[Document]:
        files = self.discover_files(directory, recursive, specific_files)
        if not files:
            return []
        policy = self._build_fallback_policy()
        documents: List[Document] = []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[SEP_DOCUMENT, SEP_SHEET, SEP_PAGE, "\n\n", "\n", " ", ""],
        )
        for file_path in files:
            suffix = Path(file_path).suffix.lower()
            if suffix in SUPPORTED_EXTENSIONS.get("pdf", []):
                try:
                    pdf_docs = process_pdf_with_qc(directory, file_path, policy)
                    documents.extend(pdf_docs)
                except Exception as exc:
                    logger.error(f"[process_directory_with_qc] Error procesando {file_path}: {exc}")
                    documents.append(
                        Document(
                            page_content=f"[EXTRACTION_FAILED] {exc}",
                            metadata={
                                "source_dir": directory,
                                "source_file": file_path,
                                "error": str(exc),
                            },
                        )
                    )
                continue
            try:
                text = self.extractor.extract_single_document(file_path)
            except Exception as exc:
                logger.error(f"[process_directory_with_qc] Error procesando {file_path}: {exc}")
                documents.append(
                    Document(
                        page_content=f"[EXTRACTION_FAILED] {exc}",
                        metadata={
                            "source_dir": directory,
                            "source_file": file_path,
                            "error": str(exc),
                        },
                    )
                )
                continue
            if not text.strip():
                continue
            base_doc = Document(
                page_content=text,
                metadata={
                    "source_dir": directory,
                    "source_file": file_path,
                    "extraction_kind": "non_pdf",
                },
            )
            chunks = splitter.split_documents([base_doc])
            for chunk in chunks:
                chunk.metadata.setdefault("source_dir", directory)
                chunk.metadata.setdefault("source_file", file_path)
                chunk.metadata.setdefault("extraction_kind", "non_pdf")
            documents.extend(chunk for chunk in chunks if chunk.page_content.strip())
        for idx_doc, document in enumerate(documents):
            document.metadata.setdefault("chunk_index", idx_doc)
        return documents
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
    def extract_directory_content(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> str:
        files = self.discover_files(directory, recursive, specific_files)
        if not files:
            logger.warning(f"[extract_directory_content] Sin archivos en {directory}")
            return ""
        logger.info(
            f"[extract_directory_content] Procesando {len(files)} archivo(s) "
            + ("específicos" if specific_files else "descubiertos")
            + f" en {directory}"
        )
        contents: List[str] = []
        for fp in files:
            content = self.extractor.extract_single_document(fp)
            if content.strip():
                contents.append(content)
        return f"\n{SEP_DOCUMENT}\n".join(contents)
    # ⬇️ FIX: añadimos directory para poder setear metadatos base
    def split_documents(self, content: str, directory: str) -> List[Document]:
        if not content.strip():
            return []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[SEP_DOCUMENT, SEP_SHEET, SEP_PAGE, "\n\n", "\n", " ", ""],
        )
        # Metadatos base para evitar struct vacío en parquet
        base_md = {"source_dir": directory}
        doc = Document(page_content=content, metadata=base_md)
        chunks = splitter.split_documents([doc])
        # Garantizar que cada chunk tenga AL MENOS una clave en metadata
        fixed: List[Document] = []
        for i, c in enumerate(chunks):
            md = dict(c.metadata or {})
            md.setdefault("source_dir", directory)
            md.setdefault("chunk_index", i)
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
            if self.table_qc:
                splits = self.extract_documents_with_qc(directory, recursive, specific_files)
            else:
                content = self.extract_directory_content(directory, recursive, specific_files)
                splits = self.split_documents(content, directory)  # ⬅️ pasa directory
            vectorstore_path = self.create_vectorstore_from_splits(splits, directory)
            return {
                "directory": directory,
                "vectorstore_path": vectorstore_path,
                "chunks_count": len(splits),
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
        "Procesa un directorio o archivo (PDF/Word/Excel/Imágenes), extrae texto, chunk-ea, "
        "vectoriza y genera un vectorstore persistente (.parquet). Devuelve JSON."
    )
    args_schema: Type[BaseModel] = RAGPipelineInput
    return_direct: bool = False
    handle_tool_error: bool = True
    def _run(
        self,
        directory: str,
        chunk_size: int = 2000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        table_qc: bool = True,
        fallback_policy: Literal["none", "repair", "annotation", "raster", "auto"] = "auto",
        suspect_threshold: float = 0.7,
        max_retry_pages: int = 4,
        annotation_schema_name: Optional[str] = None,
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
        processor = RAGProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            table_qc=table_qc,
            fallback_policy=fallback_policy,
            suspect_threshold=suspect_threshold,
            max_retry_pages=max_retry_pages,
            annotation_schema_name=annotation_schema_name,
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
        chunk_size: int = 2000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        table_qc: bool = True,
        fallback_policy: Literal["none", "repair", "annotation", "raster", "auto"] = "auto",
        suspect_threshold: float = 0.7,
        max_retry_pages: int = 4,
        annotation_schema_name: Optional[str] = None,
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
            table_qc,
            fallback_policy,
            suspect_threshold,
            max_retry_pages,
            annotation_schema_name,
            run_manager.get_sync() if run_manager else None,
        )
