from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import logging
import os
import base64
from typing import List, Dict, Any, Optional, Union, tuple
from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from PIL import Image

from src.graph.state import ValidaState
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class DocumentClassificationOutput(BaseModel):
    """Structured output for document classification by validation section"""
    
    # Linealidad
    dir_reporte_lims_linealidad: str = Field(default="", description="Directorio del reporte LIMS de Linealidad")
    dirs_hoja_trabajo_preparacion_linealidad: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Linealidad")
    dirs_hoja_trabajo_reporte_linealidad: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Linealidad")
    dirs_bitacoras_preparacion_linealidad: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Linealidad")
    dirs_bitacoras_reporte_linealidad: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Linealidad")
    
    # Precision del sistema
    dir_reporte_lims_precision_sistema: str = Field(default="", description="Directorio del reporte LIMS de Precision del Sistema")
    dirs_hoja_trabajo_preparacion_precision_sistema: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Precision del Sistema")
    dirs_hoja_trabajo_reporte_precision_sistema: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Precision del Sistema")
    dirs_bitacoras_preparacion_precision_sistema: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Precision del Sistema")
    dirs_bitacoras_reporte_precision_sistema: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Precision del Sistema")
        
    # Precision del método
    dir_reporte_lims_precision_metodo: str = Field(default="", description="Directorio del reporte LIMS de Precision del Método")
    dirs_hoja_trabajo_preparacion_precision_metodo: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Precision del Método")
    dirs_hoja_trabajo_reporte_precision_metodo: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Precision del Método")
    dirs_bitacoras_preparacion_precision_metodo: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Precision del Método")
    dirs_bitacoras_reporte_precision_metodo: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Precision del Método")
    
    # Precision Intermedia
    dir_reporte_lims_precision_intermedia: str = Field(default="", description="Directorio del reporte LIMS de Precision Intermedia")
    dirs_hoja_trabajo_preparacion_precision_intermedia: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Precision Intermedia")
    dirs_hoja_trabajo_reporte_precision_intermedia: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Precision Intermedia")        
    dirs_bitacoras_preparacion_precision_intermedia: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Precision Intermedia")
    dirs_bitacoras_reporte_precision_intermedia: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Precision Intermedia")
    
    # Exactitud
    dir_reporte_lims_exactitud: str = Field(default="", description="Directorio del reporte LIMS de Exactitud del método")
    dirs_hoja_trabajo_preparacion_exactitud: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Exactitud")
    dirs_hoja_trabajo_reporte_exactitud: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Exactitud")
    dirs_bitacoras_preparacion_exactitud: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Exactitud")
    dirs_bitacoras_reporte_exactitud: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Exactitud")
    
    # Estabilidad de la solución estandar
    dir_reporte_lims_estabilidad_solucion_estandar: str = Field(default="", description="Directorio del reporte LIMS de Estabilidad de la solución estandar")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_estandar: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la solución estandar")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_estandar: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la solución estandar")
    dirs_bitacoras_preparacion_estabilidad_solucion_estandar: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Estabilidad de la solución estandar")
    dirs_bitacoras_reporte_estabilidad_solucion_estandar: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Estabilidad de la solución estandar")
    
    # Estabilidad de la solución muestra
    dir_reporte_lims_estabilidad_solucion_muestra: str = Field(default="", description="Directorio del reporte LIMS de Estabilidad de la solución muestra")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_muestra: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la solución muestra")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_muestra: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la solución muestra")
    dirs_bitacoras_preparacion_estabilidad_solucion_muestra: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Estabilidad de la solución muestra")
    dirs_bitacoras_reporte_estabilidad_solucion_muestra: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Estabilidad de la solución muestra")
    
    # Estabilidad de la fase móvil
    dir_reporte_lims_estabilidad_solucion_fase_movil: str = Field(default="", description="Directorio del reporte LIMS de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_fase_movil: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_fase_movil: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la fase móvil")
    dirs_bitacoras_preparacion_estabilidad_solucion_fase_movil: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Estabilidad de la fase móvil")
    dirs_bitacoras_reporte_estabilidad_solucion_fase_movil: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Estabilidad de la fase móvil")

    # Robustez
    dir_reporte_lims_robustez: str = Field(default="", description="Directorio del reporte LIMS de Robustez del método")
    dirs_hoja_trabajo_preparacion_robustez: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Preparación de Robustez")
    dirs_hoja_trabajo_reporte_robustez: List[str] = Field(default_factory=list, description="Directorios de las Hojas de Trabajo de Reporte de Robustez")
    dirs_bitacoras_preparacion_robustez: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Preparación de Robustez")
    dirs_bitacoras_reporte_robustez: List[str] = Field(default_factory=list, description="Directorios de las Bitacoras de Reporte de Robustez")

class AgentUIOutput(BaseModel):
    hand_off_to_research_supervisor: bool
    documents_sufficient: bool
    missing_documents: list[str] = []

class AgentUI:
    """Agent UI that classifies validation documents and manages workflow"""
    
    CLASSIFICATION_PROMPT = """
Eres un experto en clasificación de documentos de validación farmacéutica. Tu tarea es analizar el contenido de documentos y clasificarlos en las siguientes categorías:

1. **Reporte LIMS**: Reportes generados por el sistema LIMS (Laboratory Information Management System)
2. **Hoja de Trabajo de Preparación**: Documentos que describen la preparación de soluciones, estándares, muestras
3. **Hoja de Trabajo de Reporte**: Documentos que contienen resultados y análisis de ensayos
4. **Bitácora de Preparación**: Registros de actividades de preparación realizadas
5. **Bitácora de Reporte**: Registros de actividades de reporte y análisis

Además, debes identificar a qué sección de validación pertenece cada documento:
- Linealidad
- Precision del Sistema
- Precision del Método  
- Precision Intermedia
- Exactitud
- Estabilidad de la Solución Estándar
- Estabilidad de la Solución Muestra
- Estabilidad de la Fase Móvil
- Robustez

**INSTRUCCIONES:**
1. Analiza el contenido de cada documento proporcionado
2. Identifica palabras clave, títulos, encabezados que indiquen el tipo de documento
3. Determina la sección de validación correspondiente
4. Clasifica cada documento en la categoría apropiada
5. Si un documento no puede ser clasificado claramente, déjalo sin asignar (campo vacío)

**CRITERIOS DE CLASIFICACIÓN:**
- **Reporte LIMS**: Contiene datos tabulares, resultados numéricos, códigos de muestra, timestamps del sistema
- **Hoja de Trabajo de Preparación**: Incluye procedimientos, fórmulas, cálculos de preparación, materiales
- **Hoja de Trabajo de Reporte**: Contiene análisis de resultados, gráficos, conclusiones, interpretaciones
- **Bitácora de Preparación**: Registros cronológicos de actividades de preparación, firmas, fechas
- **Bitácora de Reporte**: Registros de actividades de análisis y reporte, revisiones, aprobaciones

Responde ÚNICAMENTE con la estructura JSON solicitada, sin texto adicional.
"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            timeout=300
        )
    
    def run(self, state: ValidaState, config: RunnableConfig):
        configurable = config.get("configurable", {})        
        template_sets = configurable.get("template_sets", {})
        
        # Extract directory information from state
        state_directories = {
            "dirs_linealidad": state.get("dirs_linealidad", []),
            "dirs_precision_sistema": state.get("dirs_precision_sistema", []),
            "dirs_precision_metodo": state.get("dirs_precision_metodo", []),
            "dirs_precision_intermedia": state.get("dirs_precision_intermedia", []),
            "dirs_exactitud": state.get("dirs_exactitud", []),
            "dirs_estabilidad_solucion_estandar": state.get("dirs_estabilidad_solucion_estandar", []),
            "dirs_estabilidad_solucion_muestra": state.get("dirs_estabilidad_solucion_muestra", []),
            "dirs_estabilidad_solucion_fase_movil": state.get("dirs_estabilidad_solucion_fase_movil", []),
            "dirs_robustez": state.get("dirs_robustez", [])
        }
        
        try:
            # Classify documents using LLM
            logger.info("Starting document classification process...")
            classification_result = self._classify_documents_from_state(state_directories)
            
            # Evaluate if documents are sufficient for workflow
            documents_sufficient, missing_docs = self._evaluate_document_sufficiency(classification_result)
            
            response = AgentUIOutput(
                hand_off_to_research_supervisor=documents_sufficient,
                documents_sufficient=documents_sufficient,
                missing_documents=missing_docs
            )
            
        except Exception as e:
            logger.error(f"Error in document classification: {e}")
            # On error, assume documents are sufficient to continue workflow
            classification_result = DocumentClassificationOutput()
            response = AgentUIOutput(
                hand_off_to_research_supervisor=True,
                documents_sufficient=True,
                missing_documents=[]
            )
        
        goto_parallelized = [
            Send(
                "supervisor_research_validation",
                {
                    "messages": [
                        HumanMessage(
                            content=template_sets[set_name]["human_message_prompt"],
                            name = f"Request from {set_name}"
                        )
                    ],
                    "set_name": set_name,
                    "doc_path_list": template_sets[set_name]["doc_path_list"],
                    "data_extraction_model_key": template_sets[set_name]["data_extraction_model_key"],
                    "data_rendering_model_key": template_sets[set_name]["data_rendering_model_key"],
                    "structured_output_supervisor": template_sets[set_name]["structured_output_supervisor"],
                }
            )
            for set_name in template_sets.keys()
        ]
        
        # Prepare update dictionary with classified document paths
        update_dict = {
            "messages": [
                SystemMessage(content=f"Document classification completed. Documents sufficient: {response.documents_sufficient}")
            ],
            # Update state with classified document paths
            "dir_reporte_lims_linealidad": classification_result.dir_reporte_lims_linealidad,
            "dirs_hoja_trabajo_preparacion_linealidad": classification_result.dirs_hoja_trabajo_preparacion_linealidad,
            "dirs_hoja_trabajo_reporte_linealidad": classification_result.dirs_hoja_trabajo_reporte_linealidad,
            "dirs_bitacoras_preparacion_linealidad": classification_result.dirs_bitacoras_preparacion_linealidad,
            "dirs_bitacoras_reporte_linealidad": classification_result.dirs_bitacoras_reporte_linealidad,
            
            "dir_reporte_lims_precision_sistema": classification_result.dir_reporte_lims_precision_sistema,
            "dirs_hoja_trabajo_preparacion_precision_sistema": classification_result.dirs_hoja_trabajo_preparacion_precision_sistema,
            "dirs_hoja_trabajo_reporte_precision_sistema": classification_result.dirs_hoja_trabajo_reporte_precision_sistema,
            "dirs_bitacoras_preparacion_precision_sistema": classification_result.dirs_bitacoras_preparacion_precision_sistema,
            "dirs_bitacoras_reporte_precision_sistema": classification_result.dirs_bitacoras_reporte_precision_sistema,
            
            "dir_reporte_lims_precision_metodo": classification_result.dir_reporte_lims_precision_metodo,
            "dirs_hoja_trabajo_preparacion_precision_metodo": classification_result.dirs_hoja_trabajo_preparacion_precision_metodo,
            "dirs_hoja_trabajo_reporte_precision_metodo": classification_result.dirs_hoja_trabajo_reporte_precision_metodo,
            "dirs_bitacoras_preparacion_precision_metodo": classification_result.dirs_bitacoras_preparacion_precision_metodo,
            "dirs_bitacoras_reporte_precision_metodo": classification_result.dirs_bitacoras_reporte_precision_metodo,
            
            "dir_reporte_lims_precision_intermedia": classification_result.dir_reporte_lims_precision_intermedia,
            "dirs_hoja_trabajo_preparacion_precision_intermedia": classification_result.dirs_hoja_trabajo_preparacion_precision_intermedia,
            "dirs_hoja_trabajo_reporte_precision_intermedia": classification_result.dirs_hoja_trabajo_reporte_precision_intermedia,
            "dirs_bitacoras_preparacion_precision_intermedia": classification_result.dirs_bitacoras_preparacion_precision_intermedia,
            "dirs_bitacoras_reporte_precision_intermedia": classification_result.dirs_bitacoras_reporte_precision_intermedia,
            
            "dir_reporte_lims_exactitud": classification_result.dir_reporte_lims_exactitud,
            "dirs_hoja_trabajo_preparacion_exactitud": classification_result.dirs_hoja_trabajo_preparacion_exactitud,
            "dirs_hoja_trabajo_reporte_exactitud": classification_result.dirs_hoja_trabajo_reporte_exactitud,
            "dirs_bitacoras_preparacion_exactitud": classification_result.dirs_bitacoras_preparacion_exactitud,
            "dirs_bitacoras_reporte_exactitud": classification_result.dirs_bitacoras_reporte_exactitud,
            
            "dir_reporte_lims_estabilidad_solucion_estandar": classification_result.dir_reporte_lims_estabilidad_solucion_estandar,
            "dirs_hoja_trabajo_preparacion_estabilidad_solucion_estandar": classification_result.dirs_hoja_trabajo_preparacion_estabilidad_solucion_estandar,
            "dirs_hoja_trabajo_reporte_estabilidad_solucion_estandar": classification_result.dirs_hoja_trabajo_reporte_estabilidad_solucion_estandar,
            "dirs_bitacoras_preparacion_estabilidad_solucion_estandar": classification_result.dirs_bitacoras_preparacion_estabilidad_solucion_estandar,
            "dirs_bitacoras_reporte_estabilidad_solucion_estandar": classification_result.dirs_bitacoras_reporte_estabilidad_solucion_estandar,
            
            "dir_reporte_lims_estabilidad_solucion_muestra": classification_result.dir_reporte_lims_estabilidad_solucion_muestra,
            "dirs_hoja_trabajo_preparacion_estabilidad_solucion_muestra": classification_result.dirs_hoja_trabajo_preparacion_estabilidad_solucion_muestra,
            "dirs_hoja_trabajo_reporte_estabilidad_solucion_muestra": classification_result.dirs_hoja_trabajo_reporte_estabilidad_solucion_muestra,
            "dirs_bitacoras_preparacion_estabilidad_solucion_muestra": classification_result.dirs_bitacoras_preparacion_estabilidad_solucion_muestra,
            "dirs_bitacoras_reporte_estabilidad_solucion_muestra": classification_result.dirs_bitacoras_reporte_estabilidad_solucion_muestra,
            
            "dir_reporte_lims_estabilidad_solucion_fase_movil": classification_result.dir_reporte_lims_estabilidad_solucion_fase_movil,
            "dirs_hoja_trabajo_preparacion_estabilidad_solucion_fase_movil": classification_result.dirs_hoja_trabajo_preparacion_estabilidad_solucion_fase_movil,
            "dirs_hoja_trabajo_reporte_estabilidad_solucion_fase_movil": classification_result.dirs_hoja_trabajo_reporte_estabilidad_solucion_fase_movil,
            "dirs_bitacoras_preparacion_estabilidad_solucion_fase_movil": classification_result.dirs_bitacoras_preparacion_estabilidad_solucion_fase_movil,
            "dirs_bitacoras_reporte_estabilidad_solucion_fase_movil": classification_result.dirs_bitacoras_reporte_estabilidad_solucion_fase_movil,
            
            "dir_reporte_lims_robustez": classification_result.dir_reporte_lims_robustez,
            "dirs_hoja_trabajo_preparacion_robustez": classification_result.dirs_hoja_trabajo_preparacion_robustez,
            "dirs_hoja_trabajo_reporte_robustez": classification_result.dirs_hoja_trabajo_reporte_robustez,
            "dirs_bitacoras_preparacion_robustez": classification_result.dirs_bitacoras_preparacion_robustez,
            "dirs_bitacoras_reporte_robustez": classification_result.dirs_bitacoras_reporte_robustez,
        }
        
        if response.hand_off_to_research_supervisor:
            goto = goto_parallelized
        else:
            goto = "__end__"
        
        return Command(
            update=update_dict,
            goto=goto
        )
    
    def _evaluate_document_sufficiency(self, classification: DocumentClassificationOutput) -> tuple[bool, list[str]]:
        """Evaluate if classified documents are sufficient to proceed with validation workflow"""
        missing_documents = []
        
        # Define minimum required documents for each validation section
        required_sections = [
            ("linealidad", classification.dir_reporte_lims_linealidad),
            ("precision_sistema", classification.dir_reporte_lims_precision_sistema),
            ("precision_metodo", classification.dir_reporte_lims_precision_metodo),
            ("exactitud", classification.dir_reporte_lims_exactitud)
        ]
        
        # Check if at least LIMS reports are available for core sections
        for section_name, lims_report in required_sections:
            if not lims_report:
                missing_documents.append(f"Reporte LIMS de {section_name}")
        
        # Consider documents sufficient if we have at least 2 core LIMS reports
        documents_sufficient = len(missing_documents) <= 2
        
        return documents_sufficient, missing_documents
    
    # Document extraction methods
    def _pdf_first_page_to_base64(self, path: str) -> Optional[str]:
        """Extract first page of PDF as base64 for OCR processing"""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(path)
            if len(doc) == 0:
                return None
            
            # Get first page
            page = doc[0]
            # Convert to image
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            
            # Convert to base64
            b64_string = base64.b64encode(img_data).decode()
            doc.close()
            return b64_string
        except Exception as e:
            logger.warning(f"Error extracting first page from PDF {path}: {e}")
            return None
    
    def _extract_pdf_first_page(self, path: str) -> str:
        """Extract text content from first page of PDF using OCR"""
        try:
            # For now, return a placeholder - in production this would use Mistral OCR
            # or another OCR service to extract text from the first page
            b64_content = self._pdf_first_page_to_base64(path)
            if b64_content:
                return f"[PDF FIRST PAGE CONTENT FROM: {os.path.basename(path)}]"
            return ""
        except Exception as e:
            logger.warning(f"Error processing PDF {path}: {e}")
            return ""
    
    def _extract_word_first_page(self, path: str) -> str:
        """Extract content from first page/section of Word document"""
        try:
            docs = UnstructuredWordDocumentLoader(path).load()
            if not docs:
                return ""
            
            # Get first document content (usually represents first page/section)
            first_content = docs[0].page_content
            
            # Limit to first 2000 characters to focus on header/beginning content
            return first_content[:2000] if first_content else ""
        except Exception as e:
            logger.warning(f"Error processing Word document {path}: {e}")
            return ""
    
    def _extract_excel_first_sheet(self, path: str) -> str:
        """Extract content from first sheet of Excel file"""
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext not in (".xls", ".xlsx", ".xlsm"):
                return ""
            
            engine = "xlrd" if ext == ".xls" else "openpyxl"
            xls = pd.ExcelFile(path, engine=engine)
            
            if not xls.sheet_names:
                return ""
            
            # Get first sheet
            first_sheet_name = xls.sheet_names[0]
            df = xls.parse(first_sheet_name, nrows=20)  # Limit to first 20 rows
            
            # Convert to string representation
            csv_content = df.to_csv(sep='\t', index=False)
            return f"SHEET: {first_sheet_name}\n{csv_content}"
        except Exception as e:
            logger.warning(f"Error processing Excel file {path}: {e}")
            return ""
    
    def _extract_image_content(self, path: str) -> str:
        """Extract basic info from image file"""
        try:
            with Image.open(path) as img:
                # Return basic image info - in production this could use OCR
                return f"[IMAGE FILE: {os.path.basename(path)}, Size: {img.size}, Format: {img.format}]"
        except Exception as e:
            logger.warning(f"Error processing image {path}: {e}")
            return ""
    
    def _extract_first_page_content(self, file_path: str) -> str:
        """Extract first page/sheet content from any supported document format"""
        if not os.path.exists(file_path):
            return ""
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".pdf":
                return self._extract_pdf_first_page(file_path)
            elif ext in (".doc", ".docx"):
                return self._extract_word_first_page(file_path)
            elif ext in (".xls", ".xlsx", ".xlsm"):
                return self._extract_excel_first_sheet(file_path)
            elif ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif"):
                return self._extract_image_content(file_path)
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return f"[UNSUPPORTED FORMAT: {ext}]"
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {e}")
            return ""
    
    def _extract_multiple_first_pages(self, file_paths: List[str]) -> List[tuple[str, str]]:
        """Extract first page content from multiple files
        
        Returns:
            List of tuples (file_path, content)
        """
        results = []
        for file_path in file_paths:
            content = self._extract_first_page_content(file_path)
            results.append((file_path, content))
        return results
    
    # Document classification methods
    def _extract_documents_content(self, directory_lists: Dict[str, List[str]]) -> Dict[str, List[tuple[str, str]]]:
        """Extract first page content from all documents in directory lists"""
        all_documents = {}
        
        for section_name, file_paths in directory_lists.items():
            if not file_paths:
                all_documents[section_name] = []
                continue
                
            # Flatten file paths if nested
            flat_paths = []
            for path in file_paths:
                if os.path.isdir(path):
                    # If it's a directory, get all files in it
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            flat_paths.append(file_path)
                else:
                    flat_paths.append(path)
            
            # Extract content from each document
            documents_content = self._extract_multiple_first_pages(flat_paths)
            all_documents[section_name] = documents_content
            
        return all_documents
    
    def _create_classification_prompt(self, documents_content: Dict[str, List[tuple[str, str]]]) -> str:
        """Create the classification prompt with document contents"""
        prompt_parts = [self.CLASSIFICATION_PROMPT]
        prompt_parts.append("\n**DOCUMENTOS A CLASIFICAR:**\n")
        
        for section_name, docs in documents_content.items():
            if not docs:
                continue
                
            prompt_parts.append(f"\n--- SECCIÓN: {section_name.upper()} ---")
            for i, (file_path, content) in enumerate(docs, 1):
                filename = os.path.basename(file_path)
                prompt_parts.append(f"\nDocumento {i}: {filename}")
                prompt_parts.append(f"Ruta: {file_path}")
                prompt_parts.append(f"Contenido: {content[:1000]}...")  # Limit content length
                prompt_parts.append("---")
        
        return "\n".join(prompt_parts)
    
    def _classify_documents(self, directory_lists: Dict[str, List[str]]) -> DocumentClassificationOutput:
        """Classify documents from directory lists into validation categories"""
        try:
            # Extract content from all documents
            documents_content = self._extract_documents_content(directory_lists)
            
            # Create classification prompt
            classification_prompt = self._create_classification_prompt(documents_content)
            
            # Create messages for LLM
            messages = [
                SystemMessage(content="Eres un experto clasificador de documentos de validación farmacéutica."),
                HumanMessage(content=classification_prompt)
            ]
            
            # Get structured response from LLM
            structured_llm = self.llm.with_structured_output(DocumentClassificationOutput)
            result = structured_llm.invoke(messages)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in document classification: {e}")
            # Return empty classification on error
            return DocumentClassificationOutput()
    
    def _classify_documents_from_state(self, state_directories: Dict[str, Any]) -> DocumentClassificationOutput:
        """Classify documents from state directory information"""
        # Extract directory lists from state
        directory_lists = {
            "linealidad": state_directories.get("dirs_linealidad", []),
            "precision_sistema": state_directories.get("dirs_precision_sistema", []),
            "precision_metodo": state_directories.get("dirs_precision_metodo", []),
            "precision_intermedia": state_directories.get("dirs_precision_intermedia", []),
            "exactitud": state_directories.get("dirs_exactitud", []),
            "estabilidad_solucion_estandar": state_directories.get("dirs_estabilidad_solucion_estandar", []),
            "estabilidad_solucion_muestra": state_directories.get("dirs_estabilidad_solucion_muestra", []),
            "estabilidad_solucion_fase_movil": state_directories.get("dirs_estabilidad_solucion_fase_movil", []),
            "robustez": state_directories.get("dirs_robustez", [])
        }
        
        return self._classify_documents(directory_lists)