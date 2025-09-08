from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from src.graph.nodes.supervisor_research_validation.state import SupervisorResearchValidationOutput
from typing import Annotated, List, Dict, Any
from pydantic import Field, BaseModel
import operator

class SupervisorResearchValidationOutput(BaseModel):
    set_name: str = Field(..., description="Name of the tag set")
    context_for_set: Dict[str, Any] = Field(..., description="Context for the tag set")


class API(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    concentracion: str = Field(..., description="Concentración del ingrediente activo")

class ValidaState(AgentStateWithStructuredResponse):
    """Estado del Sistema Agentico Valida"""
    validacion: str = Field(..., description="Nombre del reporte de validación")
    codigo_informe: str = Field(..., description="Código del informe de validación")
    nombre_producto: str = Field(..., description="Nombre del producto cuyo método anlítico está siendo validado")
    codigo_producto: str = Field(..., description="Código del producto cuyo método anlítico está siendo validado")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos del producto cuyo metodo esta siendo validado")
    rango_validado: str = Field(..., description="Rango de validación del método analítico")
    
    # Protocolo de validación
    dir_protocolo: str = Field(..., description="Directorio del protocolo de validació del método analítico")
    
    # Linealidad
    dirs_linealidad: List[str] = Field(..., description="Directorios de la Linealidad")
    dir_reporte_lims_linealidad: str = Field(..., description="Directorio del reporte LIMS de Linealidad")
    dirs_hoja_trabajo_preparacion_linealidad: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Linealidad")
    dirs_hoja_trabajo_reporte_linealidad: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Linealidad")
    dirs_bitacoras_preparacion_linealidad: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Linealidad")
    dirs_bitacoras_reporte_linealidad: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Linealidad")
    
    # Precision del sistema
    dirs_precision_sistema: List[str] = Field(..., description="Directorios de la Precision del Sistema")
    dir_reporte_lims_precision_sistema: str = Field(..., description="Directorio del reporte LIMS de Precision del Sistema")
    dirs_hoja_trabajo_preparacion_precision_sistema: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Precision del Sistema")
    dirs_hoja_trabajo_reporte_precision_sistema: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Precision del Sistema")
    dirs_bitacoras_preparacion_precision_sistema: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Precision del Sistema")
    dirs_bitacoras_reporte_precision_sistema: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Precision del Sistema")
        
    # Precision del método
    dirs_precision_metodo: List[str] = Field(..., description="Directorios de la Precision del Método")
    dir_reporte_lims_precision_metodo: str = Field(..., description="Directorio del reporte LIMS de Precision del Método")
    dirs_hoja_trabajo_preparacion_precision_metodo: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Precision del Método")
    dirs_hoja_trabajo_reporte_precision_metodo: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Precision del Método")
    dirs_bitacoras_preparacion_precision_metodo: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Precision del Método")
    dirs_bitacoras_reporte_precision_metodo: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Precision del Método")
    
    # Precision Intermedia
    dirs_precision_intermedia: List[str] = Field(..., description="Directorios de la Precision Intermedia")
    dir_reporte_lims_precision_intermedia: str = Field(..., description="Directorio del reporte LIMS de Precision Intermedia")
    dirs_hoja_trabajo_preparacion_precision_intermedia: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Precision Intermedia")
    dirs_hoja_trabajo_reporte_precision_intermedia: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Precision Intermedia")        
    dirs_bitacoras_preparacion_precision_intermedia: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Precision Intermedia")
    dirs_bitacoras_reporte_precision_intermedia: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Precision Intermedia")
    
    # Exactitud
    dirs_exactitud: List[str] = Field(..., description="Directorios de la Exactitud")
    dir_reporte_lims_exactitud: str = Field(..., description="Directorio del reporte LIMS de Exactitud del método")
    dirs_hoja_trabajo_preparacion_exactitud: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Exactitud")
    dirs_hoja_trabajo_reporte_exactitud: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Exactitud")
    dirs_bitacoras_preparacion_exactitud: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Exactitud")
    dirs_bitacoras_reporte_exactitud: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Exactitud")
    
    # Estabilidad de la solución estandar
    dirs_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de la Estabilidad de la solución estandar")
    dir_reporte_lims_estabilidad_solucion_estandar: str = Field(..., description="Directorio del reporte LIMS de Estabilidad de la solución estandar")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la solución estandar")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la solución estandar")
    dirs_bitacoras_preparacion_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Estabilidad de la solución estandar")
    dirs_bitacoras_reporte_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Estabilidad de la solución estandar")
    
    # Estabilidad de la solución muestra
    dirs_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de la Estabilidad de la solución muestra")
    dir_reporte_lims_estabilidad_solucion_muestra: str = Field(..., description="Directorio del reporte LIMS de Estabilidad de la solución muestra")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la solución muestra")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la solución muestra")
    dirs_bitacoras_preparacion_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Estabilidad de la solución muestra")
    dirs_bitacoras_reporte_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Estabilidad de la solución muestra")
    
    # Estabilidad de la fase móvil
    dirs_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de la Estabilidad de la fase móvil")
    dir_reporte_lims_estabilidad_solucion_fase_movil: str = Field(..., description="Directorio del reporte LIMS de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_preparacion_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_reporte_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Estabilidad de la fase móvil")
    dirs_bitacoras_preparacion_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Estabilidad de la fase móvil")
    dirs_bitacoras_reporte_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Estabilidad de la fase móvil")

    # Robustez
    dirs_robustez: List[str] = Field(..., description="Directorios de la Robustez")
    dir_reporte_lims_robustez: str = Field(..., description="Directorio del reporte LIMS de Robustez del método")
    dirs_hoja_trabajo_preparacion_robustez: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación de Robustez")
    dirs_hoja_trabajo_reporte_robustez: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Reporte de Robustez")
    dirs_bitacoras_preparacion_robustez: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación de Robustez")
    dirs_bitacoras_reporte_robustez: List[str] = Field(..., description="Directorios de las Bitacoras de Reporte de Robustez")
    
    
    context_for_render: Annotated[List[SupervisorResearchValidationOutput], operator.add]
    