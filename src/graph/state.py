from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from enum import Enum
from typing import Annotated, List, Dict, Any, Optional, Union, Iterator
from pydantic import Field, BaseModel
import operator

class IndexNodeOutput(BaseModel):
    document_name: str  # Solo el nombre del archivo, sin ruta
    extracted_content: Any  # Instancia del modelo Pydantic data_extraction_model

class SupervisorResearchValidationOutput(BaseModel):
    set_name: str = Field(..., description="Name of the tag set")
    context_for_set: Dict[str, Any] = Field(..., description="Context for the tag set")


class API(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    concentracion: str = Field(..., description="Concentración del ingrediente activo")


class FileDescriptor(BaseModel):
    name: str = Field(..., description="Nombre del archivo tal como fue cargado")
    url: str = Field(..., description="URL accesible para descargar el archivo")
    size: int = Field(..., description="Tamano del archivo en bytes")
    content_type: str = Field(..., description="Tipo MIME reportado para el archivo")
    source_id: Optional[str] = Field(None, description="Identificador interno opcional del repositorio origen")
    checksum: Optional[str] = Field(None, description="Checksum opcional para validar integridad")


class RenderedReport(BaseModel):
    name: str = Field(..., description="Nombre del archivo generado")
    path: str = Field(..., description="Ruta local donde se guardó el archivo")
    content_type: str = Field(..., description="Tipo MIME del archivo generado")
    size: int = Field(..., description="Tamano del archivo en bytes")
    content_base64: Optional[str] = Field(None, description="Contenido del archivo en base64 cuando no supera el límite configurado")
    content_error: Optional[str] = Field(None, description="Mensaje de error si no se pudo adjuntar el contenido en base64")


class DocumentGroupName(str, Enum):
    PROTOCOLO = "Protocolo"
    HOJAS_TRABAJO_PREPARACION = "Hojas de Trabajo Preparacion"
    PREPARACION_BITACORAS = "Preparacion Bitacoras"
    LINEALIDAD = "Linealidad"
    PRECISION_SISTEMA = "Precision del sistema"
    PRECISION_METODO = "Precision del método"
    PRECISION_INTERMEDIA = "Precision Intermedia"
    EXACTITUD = "Exactitud"
    ESTABILIDAD_SOLUCION = "Estabilidad solución"
    ESTABILIDAD_FASE_MOVIL = "Estabilidad fase móvil"
    ROBUSTEZ = "Robustez"


class DocumentName(str, Enum):
    PROTOCOLO = "Protocolo"
    HOJAS_TRABAJO_PREPARACION = "Hojas de Trabajo Preparacion"
    PREPARACION_BITACORAS = "Preparacion Bitacoras"
    REPORTE_LIMS = "Reporte LIMS"
    HOJAS_TRABAJO = "Hojas de Trabajo"
    BITACORAS = "Bitacoras"
    SOPORTES_CROMATOGRAFICOS = "Soportes Cromatográficos"


class DocumentGroup(BaseModel):
    group: DocumentGroupName = Field(..., description="Grupo temático de documentos")
    document: DocumentName = Field(..., description="Subtipo de documento dentro del grupo")
    files: List[FileDescriptor] = Field(default_factory=list, description="Listado de archivos asociados al grupo y subtipo")

class ValidaState(AgentStateWithStructuredResponse):
    """Estado del Sistema Agentico Valida"""
    validacion: str = Field(..., description="Nombre del reporte de validación")
    codigo_informe: str = Field(..., description="Código del informe de validación")
    nombre_producto: str = Field(..., description="Nombre del producto cuyo método anlítico está siendo validado")
    codigo_producto: str = Field(..., description="Código del producto cuyo método anlítico está siendo validado")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos del producto cuyo metodo esta siendo validado")
    rango_validado: str = Field(..., description="Rango de validación del método analítico")
    document_groups: List[DocumentGroup] = Field(default_factory=list, description="Colecciones de archivos agrupados por tipo de documento")
    
    # Protocolo de validación
    dir_protocolo: FileDescriptor = Field(..., description="Directorio del protocolo de validació del método analítico")
    
    # Hojas de trabajo y bitácoras de preparación
    dir_hoja_trabajo_preparacion: List[FileDescriptor] = Field(..., description = "Listado de las rutas de las hojas de trabajo de preparación para todos los parámetros de validación")
    dirs_bitacora_preparacion: List[FileDescriptor] = Field(..., description="Listado de las rutas de las bitacoras de preparación para todos los parámetros de validación")
    
    # Linealidad
    dir_reporte_lims_linealidad: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Linealidad")
    dirs_hoja_trabajo_linealidad: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Linealidad")
    dirs_bitacoras_linealidad: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Linealidad")
    dirs_soportes_cromatograficos_linealidad: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Linealidad")
    
    # Precision del sistema
    dir_reporte_lims_precision_sistema: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Precision del Sistema")
    dirs_hoja_trabajo_precision_sistema: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Precision del Sistema")
    dirs_bitacoras_precision_sistema: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Precision del Sistema")
    dirs_soportes_cromatograficos_precision_sistema: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision del Sistema")        
    
    # Precision del método
    dir_reporte_lims_precision_metodo: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Precision del Método")
    dirs_hoja_trabajo_precision_metodo: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Precision del Método")
    dirs_bitacoras_precision_metodo: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Precision del Método")
    dirs_soportes_cromatograficos_precision_metodo: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision del Método")
    
    # Precision Intermedia
    dir_reporte_lims_precision_intermedia: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Precision Intermedia")
    dirs_hoja_trabajo_precision_intermedia: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Precision Intermedia")
    dirs_bitacoras_precision_intermedia: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Precision Intermedia")
    dirs_soportes_cromatograficos_precision_intermedia: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision Intermedia")
    
    # Exactitud
    dir_reporte_lims_exactitud: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Exactitud del método")
    dirs_hoja_trabajo_exactitud: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Exactitud")
    dirs_bitacoras_exactitud: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Exactitud")
    dirs_soportes_cromatograficos_exactitud: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Exactitud")
    
    # Estabilidad de la solución
    dir_reporte_lims_estabilidad_solucion: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Estabilidad de la solución")
    dirs_hoja_trabajo_estabilidad_solucion: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Estabilidad de la solución")
    dirs_bitacoras_estabilidad_solucion: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Estabilidad de la solución")
    dirs_soportes_cromatograficos_estabilidad_solucion: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Estabilidad de la solución")
    
    # Estabilidad de la fase móvil
    dir_reporte_lims_estabilidad_solucion_fase_movil: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_estabilidad_solucion_fase_movil: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Estabilidad de la fase móvil")
    dirs_bitacoras_estabilidad_solucion_fase_movil: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Estabilidad de la fase móvil")
    dirs_soportes_cromatograficos_estabilidad_solucion_fase_movil: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Estabilidad de la fase móvil")

    # Robustez
    dir_reporte_lims_robustez: List[FileDescriptor] = Field(..., description="Directorio del reporte LIMS de Robustez del método")
    dirs_hoja_trabajo_robustez: List[FileDescriptor] = Field(..., description="Directorios de las Hojas de Trabajo de Robustez")
    dirs_bitacoras_robustez: List[FileDescriptor] = Field(..., description="Directorios de las Bitacoras de Robustez")
    dirs_soportes_cromatograficos_robustez: List[FileDescriptor] = Field(..., description="Directorios de los Soportes Cromatográficos de Robustez")

    extraction_content: Annotated[List[IndexNodeOutput], operator.add]
    
    context_for_render: Annotated[List[SupervisorResearchValidationOutput], operator.add]
    fname_out: str = Field(..., description="Nombre del archivo de salida")
    rendered_report: Optional[RenderedReport] = Field(None, description="Metadatos del reporte DOCX generado por el sistema")
    
