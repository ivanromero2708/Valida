from __future__ import annotations
"""
RAG Pipeline Tool – Procesamiento paralelo de directorios
---------------------------------------------------------
Herramienta LangChain que recibe una lista de rutas a directorios locales y,
para cada directorio, procesa en paralelo todos los documentos soportados
(.docx, .pdf, .xls/.xlsx, imágenes), extrayendo texto vía OCR Mistral para
PDF/imágenes y loaders estándar para Word/Excel, hace chunking, vectoriza
y genera un vectorstore persistente (.parquet) por cada directorio.

Requisitos:
- mistralai (>=1.5.0)
- langchain, langchain_community, langchain_openai
- pandas, pillow, openpyxl, xlrd
- scikit-learn
- MISTRAL_API_KEY y OPENAI_API_KEY en el entorno

Devuelve JSON mapeando cada directorio a la ruta de su vectorstore generado
y logs/errores de cualquier fallo en el pipeline.
"""

import os
import base64
import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.tools import BaseTool, ToolException
from langchain_openai import OpenAIEmbeddings
from mistralai import Mistral
from mistralai.models import SDKError
from pydantic import BaseModel, Field
from langsmith import traceable
import openai

# Configuración de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Extensiones soportadas
SUPPORTED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'word': ['.doc', '.docx'],
    'excel': ['.xls', '.xlsx', '.xlsm'],
    'image': ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.webp']
}

ALL_EXTENSIONS = []
for ext_list in SUPPORTED_EXTENSIONS.values():
    ALL_EXTENSIONS.extend(ext_list)


def _create_mistral_client() -> Mistral:
    """Crea un cliente Mistral independiente por hilo para evitar problemas de concurrencia."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Defina la variable MISTRAL_API_KEY con su API-Key de Mistral AI"
        )
    return Mistral(api_key=api_key, timeout_ms=300000)


class RAGPipelineInput(BaseModel):
    """Schema de entrada para la RAG Pipeline Tool."""
    directories: List[str] = Field(
        ..., 
        description="Lista de rutas a directorios locales para procesar"
    )
    max_workers: int = Field(
        4, 
        description="Número máximo de workers para procesamiento paralelo"
    )
    chunk_size: int = Field(
        2000, 
        description="Tamaño de chunk para text splitting"
    )
    chunk_overlap: int = Field(
        250, 
        description="Overlap entre chunks"
    )
    recursive: bool = Field(
        True, 
        description="Buscar archivos recursivamente en subdirectorios"
    )
    specific_files: Optional[List[str]] = Field(
        None,
        description="Lista opcional de nombres de archivos específicos a procesar en cada directorio"
    )


class DocumentExtractor:
    """Extractor de contenido de documentos con soporte para múltiples formatos."""
    
    @staticmethod
    def _file_to_base64(path: str) -> str:
        """Convierte archivo a base64."""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    @traceable
    def extract_pdf(self, path_doc: str, ocr_model: str = "mistral-ocr-latest", retries: int = 3) -> str:
        """Extrae contenido de PDF usando OCR Mistral."""
        client = _create_mistral_client()
        b64_pdf = self._file_to_base64(path_doc)

        for attempt in range(1, retries + 1):
            try:
                ocr_response = client.ocr.process(
                    model=ocr_model,
                    document={
                        "type": "document_url",
                        "document_url": f"data:application/pdf;base64,{b64_pdf}",
                    },
                    include_image_base64=False,
                )
                break
            except SDKError as e:
                if attempt == retries or getattr(e, "status_code", 0) < 500:
                    raise
                time.sleep(2 ** (attempt - 1))
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(2 ** (attempt - 1))

        pages_markdown: List[str] = [page.markdown for page in ocr_response.pages]
        return "\n-----PAGE BREAK-----\n".join(pages_markdown)

    @traceable
    def extract_image(self, path_doc: str, ocr_model: str = "mistral-ocr-latest", retries: int = 3) -> str:
        """Extrae contenido de imagen usando OCR Mistral."""
        client = _create_mistral_client()
        
        # Detectar tipo MIME de la imagen
        ext = Path(path_doc).suffix.lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/jpeg')
        
        b64_image = self._file_to_base64(path_doc)

        for attempt in range(1, retries + 1):
            try:
                ocr_response = client.ocr.process(
                    model=ocr_model,
                    document={
                        "type": "document_url",
                        "document_url": f"data:{mime_type};base64,{b64_image}",
                    },
                    include_image_base64=False,
                )
                break
            except SDKError as e:
                if attempt == retries or getattr(e, "status_code", 0) < 500:
                    raise
                time.sleep(2 ** (attempt - 1))
            except Exception:
                if attempt == retries:
                    raise
                time.sleep(2 ** (attempt - 1))

        pages_markdown: List[str] = [page.markdown for page in ocr_response.pages]
        return "\n-----PAGE BREAK-----\n".join(pages_markdown)

    @traceable
    def extract_word(self, path_doc: str) -> str:
        """Extrae contenido de documento Word."""
        docs = UnstructuredWordDocumentLoader(path_doc).load()
        if not docs:
            raise ValueError(f"No se encontró contenido en {path_doc}")
        return "\n-----PAGE BREAK-----\n".join(doc.page_content for doc in docs)

    @traceable
    def extract_excel(self, path_doc: str) -> str:
        """Extrae contenido de archivo Excel."""
        ext = os.path.splitext(path_doc)[1].lower()
        if ext not in (".xls", ".xlsx", ".xlsm"):
            raise ValueError(f"{path_doc} no parece ser un archivo de Excel soportado.")

        engine = "xlrd" if ext == ".xls" else "openpyxl"
        try:
            xls = pd.ExcelFile(path_doc, engine=engine)
        except Exception as e:
            raise ValueError(f"No se pudo abrir el archivo {path_doc}: {e}") from e

        sheets = []
        for name in xls.sheet_names:
            df = xls.parse(name)
            csv_content = df.to_csv(sep='\t', index=False)
            sheets.append(f"--SHEET:{name}--\n{csv_content}")
            
        if not sheets:
            raise ValueError(f"No se pudo extraer contenido de {path_doc}")
        return "\n-----SHEET BREAK-----\n".join(sheets)

    @traceable
    def extract_single_document(self, path_doc: str) -> str:
        """Extrae contenido de un documento individual."""
        ext = Path(path_doc).suffix.lower()
        
        try:
            if ext in SUPPORTED_EXTENSIONS['pdf']:
                return self.extract_pdf(path_doc)
            elif ext in SUPPORTED_EXTENSIONS['word']:
                return self.extract_word(path_doc)
            elif ext in SUPPORTED_EXTENSIONS['excel']:
                return self.extract_excel(path_doc)
            elif ext in SUPPORTED_EXTENSIONS['image']:
                return self.extract_image(path_doc)
            else:
                raise ValueError(f"Extensión no soportada: {ext}")
        except Exception as e:
            logger.warning(f"[DocumentExtractor] {path_doc} → {e}")
            return ""


class RAGProcessor:
    """Procesador principal del pipeline RAG."""
    
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 250):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.extractor = DocumentExtractor()

    def discover_files(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> List[str]:
        """Descubre archivos soportados, opcionalmente filtrando por una lista específica."""
        if specific_files:
            # Usar solo los archivos específicos que existen y están soportados
            return [
                f for f in specific_files
                if Path(f).exists() and Path(f).suffix.lower() in ALL_EXTENSIONS
            ]

        directory_path = Path(directory)
        if not directory_path.is_dir():
            raise ValueError(f"La ruta {directory} no es un directorio válido")

        files = []
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in ALL_EXTENSIONS:
                files.append(str(file_path))
        return files

    def extract_directory_content(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> str:
        """Extrae contenido de archivos en un directorio, opcionalmente de una lista específica."""
        files = self.discover_files(directory, recursive, specific_files)
        
        if not files:
            logger.warning(f"No se encontraron archivos soportados para procesar en {directory}")
            return ""
        
        log_msg = f"Procesando {len(files)} archivos específicos en {directory}" if specific_files else f"Procesando {len(files)} archivos descubiertos en {directory}"
        logger.info(log_msg)
        
        contents = []
        for file_path in files:
            content = self.extractor.extract_single_document(file_path)
            if content.strip():
                contents.append(content)
        
        return "\n=====DOCUMENT BREAK=====\n".join(contents)

    def split_documents(self, content: str) -> List[Document]:
        """Divide el contenido en chunks usando RecursiveCharacterTextSplitter."""
        if not content.strip():
            return []
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "=====DOCUMENT BREAK=====",
                "-----SHEET BREAK-----",
                "-----PAGE BREAK-----",
                "\n\n",
                "\n",
                " ",
                "",
            ],
        )
        
        document = Document(page_content=content)
        chunks = splitter.split_documents([document])
        
        # Filtrar chunks vacíos
        return [chunk for chunk in chunks if chunk.page_content.strip()]

    def _safe_build_vectorstore(
        self,
        splits: List[Document],
        embeddings: OpenAIEmbeddings,
        persist_path: Path,
    ) -> SKLearnVectorStore:
        """Construye el vectorstore con manejo de errores de tokens."""
        try:
            # Crear vectorstore con persistencia directa
            vectorstore = SKLearnVectorStore.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_path=persist_path.as_posix(),
                serializer="parquet",
            )
            return vectorstore
        except openai.BadRequestError as e:
            if "max_tokens_per_request" not in str(e):
                raise

            logger.warning(
                "[RAGProcessor] Exceso de tokens → reintento con lote reducido"
            )
            smaller_embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                chunk_size=32,  # Máx. 32 docs por llamada
            )
            vectorstore = SKLearnVectorStore.from_documents(
                documents=splits,
                embedding=smaller_embeddings,
                persist_path=persist_path.as_posix(),
                serializer="parquet",
            )
            return vectorstore

    def create_vectorstore(self, splits: List[Document], directory: str) -> str:
        """Crea y persiste el vectorstore para un directorio."""
        if not splits:
            logger.warning(f"Sin contenido utilizable para {directory} → vectorstore dummy")
            splits = [
                Document(
                    page_content="Contenido no disponible para este directorio.",
                    metadata={"dummy": True, "source": directory},
                )
            ]

        # Configuración de embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            chunk_size=96,  # Máx. 96 docs por request
        )

        # Ruta de persistencia centralizada
        output_dir = Path.cwd() / "vectorstores"
        directory_name = Path(directory).name
        persist_path = output_dir / f"vectorstore_{directory_name}_{uuid.uuid4().hex[:8]}.parquet"
        
        # Crear directorio de salida si no existe
        output_dir.mkdir(exist_ok=True, parents=True)

        # Añadir metadata a cada chunk para evitar error de Parquet
        for split in splits:
            split.metadata["source"] = directory

        # Crear vectorstore
        try:
            vectorstore = self._safe_build_vectorstore(splits, embeddings, persist_path)
            vectorstore.persist()
            
            # Verificar que el archivo se creó correctamente
            if not persist_path.exists():
                raise RuntimeError(f"Error: No se pudo crear el vectorstore en {persist_path}")
            
            # Log para verificar la ruta
            logger.info(f"Vectorstore creado exitosamente en: {persist_path.as_posix()}")
            
            return persist_path.as_posix()
            
        except Exception as e:
            logger.error(f"Error detallado creando vectorstore: {e}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            logger.error(f"Directorio objetivo: {persist_path.parent}")
            logger.error(f"Archivo objetivo: {persist_path.name}")
            logger.error(f"Número de splits: {len(splits)}")
            raise RuntimeError(f"Error: No se pudo crear el vectorstore en {persist_path}") from e

    def process_directory(self, directory: str, recursive: bool = True, specific_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Procesa un directorio (o archivos específicos dentro de él) y devuelve el resultado."""
        try:
            # Extraer contenido
            content = self.extract_directory_content(directory, recursive, specific_files)
            
            # Hacer chunking
            splits = self.split_documents(content)
            
            # Crear vectorstore
            vectorstore_path = self.create_vectorstore(splits, directory)
            
            return {
                "directory": directory,
                "vectorstore_path": vectorstore_path,
                "chunks_count": len(splits),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error procesando el trabajo para {directory}: {e}")
            return {
                "directory": directory,
                "vectorstore_path": None,
                "error": str(e),
                "status": "failed"
            }


class RAGPipelineTool(BaseTool):
    """LangChain Tool para procesamiento paralelo de directorios con pipeline RAG."""
    
    name: str = "rag_pipeline_tool"
    description: str = """Procesa múltiples directorios en paralelo, extrayendo texto de documentos 
    (PDF, Word, Excel, imágenes), hace chunking, vectoriza y genera vectorstores persistentes (.parquet). 
    Devuelve JSON mapeando cada directorio a su vectorstore generado."""
    args_schema: Type[BaseModel] = RAGPipelineInput
    return_direct: bool = False
    handle_tool_error: bool = True

    def _run(
        self,
        directories: List[str],
        max_workers: int = 4,
        chunk_size: int = 2000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Ejecuta el pipeline RAG en paralelo para múltiples directorios."""
        
        if not directories:
            raise ToolException("Se requiere al menos una ruta (directorio o archivo) para procesar")

        # Normalizar entradas: agrupar archivos por directorio padre
        tasks = {}
        results = {}
        logs = []
        
        # Si se especifican archivos específicos, usarlos directamente
        if specific_files:
            for directory in directories:
                dir_path = Path(directory)
                if dir_path.exists() and dir_path.is_dir():
                    tasks[str(dir_path)] = {"specific_files": specific_files}
        else:
            # Lógica original para procesar directorios o archivos
            for path_str in directories:
                path = Path(path_str)
                if not path.exists():
                    logs.append({"directory": path_str, "error": f"La ruta no existe: {path_str}", "status": "failed"})
                    results[path_str] = None
                    continue

                if path.is_dir():
                    dir_key = str(path)
                    if dir_key not in tasks:
                        tasks[dir_key] = {"specific_files": None} # Procesar directorio completo
                elif path.is_file():
                    dir_key = str(path.parent)
                    if dir_key not in tasks:
                        tasks[dir_key] = {"specific_files": []}
                    # Asegurarse de no añadir archivos si el directorio ya está para procesamiento completo
                    if tasks[dir_key]["specific_files"] is not None:
                        tasks[dir_key]["specific_files"].append(path.name)

        processor = RAGProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Procesamiento secuencial (paralelismo deshabilitado para depuración)
        logger.warning("Ejecutando RAG Pipeline en modo secuencial (sin paralelismo).")
        for dir_path, task_info in tasks.items():
            try:
                result = processor.process_directory(
                    directory=dir_path,
                    recursive=recursive,
                    specific_files=task_info["specific_files"]
                )
                
                # Para specific_files, usar el directorio como clave
                if result["status"] == "success":
                    results[dir_path] = result["vectorstore_path"]
                    logger.info(f"✓ {dir_path} → {result['vectorstore_path']} ({result['chunks_count']} chunks)")
                else:
                    results[dir_path] = None
                    logs.append({
                        "directory": dir_path,
                        "error": result.get("error", "Unknown error"),
                        "status": "failed"
                    })

            except Exception as exc:
                logger.error(f"Error crítico procesando el directorio {dir_path}: {exc}")
                results[dir_path] = None
                logs.append({
                    "directory": dir_path,
                    "error": str(exc),
                    "status": "failed"
                })
        
        # Construir respuesta
        response = {"directories": results}
        if logs:
            response["logs"] = logs
        
        return json.dumps(response, indent=2, ensure_ascii=False)

    async def _arun(
        self,
        directories: List[str],
        max_workers: int = 4,
        chunk_size: int = 2000,
        chunk_overlap: int = 250,
        recursive: bool = True,
        specific_files: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Versión asíncrona del pipeline RAG."""
        import asyncio
        return await asyncio.to_thread(
            self._run,
            directories,
            max_workers,
            chunk_size,
            chunk_overlap,
            recursive,
            specific_files,
            run_manager.get_sync() if run_manager else None,
        )