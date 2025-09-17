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
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

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
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 250):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
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

        processor = RAGProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

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
            run_manager.get_sync() if run_manager else None,
        )
