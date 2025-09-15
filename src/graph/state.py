from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
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
    dir_reporte_lims_linealidad: List[str] = Field(..., description="Directorio del reporte LIMS de Linealidad")
    dirs_hoja_trabajo_linealidad: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Linealidad")
    dirs_bitacoras_linealidad: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Linealidad")
    dirs_soportes_cromatográficos_linealidad: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Linealidad")
    
    # Precision del sistema
    dir_reporte_lims_precision_sistema: List[str] = Field(..., description="Directorio del reporte LIMS de Precision del Sistema")
    dirs_hoja_trabajo_precision_sistema: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Precision del Sistema")
    dirs_bitacoras_precision_sistema: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Precision del Sistema")
    dirs_soportes_cromatográficos_precision_sistema: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision del Sistema")        
    
    # Precision del método
    dir_reporte_lims_precision_metodo: List[str] = Field(..., description="Directorio del reporte LIMS de Precision del Método")
    dirs_hoja_trabajo_precision_metodo: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Precision del Método")
    dirs_bitacoras_precision_metodo: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Precision del Método")
    dirs_soportes_cromatográficos_precision_metodo: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision del Método")
    
    # Precision Intermedia
    dir_reporte_lims_precision_intermedia: List[str] = Field(..., description="Directorio del reporte LIMS de Precision Intermedia")
    dirs_hoja_trabajo_precision_intermedia: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Precision Intermedia")
    dirs_bitacoras_precision_intermedia: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Precision Intermedia")
    dirs_soportes_cromatográficos_precision_intermedia: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Precision Intermedia")
    
    # Exactitud
    dir_reporte_lims_exactitud: List[str] = Field(..., description="Directorio del reporte LIMS de Exactitud del método")
    dirs_hoja_trabajo_exactitud: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Exactitud")
    dirs_bitacoras_exactitud: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Exactitud")
    dirs_soportes_cromatográficos_exactitud: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Exactitud")
    
    # Estabilidad de la solución estandar
    dir_reporte_lims_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorio del reporte LIMS de Estabilidad de la solución estandar")
    dirs_hoja_trabajo_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Estabilidad de la solución estandar")
    dirs_bitacoras_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Estabilidad de la solución estandar")
    dirs_soportes_cromatográficos_estabilidad_solucion_estandar: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Estabilidad de la solución estandar")
    
    # Estabilidad de la solución muestra
    dir_reporte_lims_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorio del reporte LIMS de Estabilidad de la solución muestra")
    dirs_hoja_trabajo_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Estabilidad de la solución muestra")
    dirs_bitacoras_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Estabilidad de la solución muestra")
    dirs_soportes_cromatográficos_estabilidad_solucion_muestra: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Estabilidad de la solución muestra")
    
    # Estabilidad de la fase móvil
    dir_reporte_lims_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorio del reporte LIMS de Estabilidad de la fase móvil")
    dirs_hoja_trabajo_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Estabilidad de la fase móvil")
    dirs_bitacoras_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Estabilidad de la fase móvil")
    dirs_soportes_cromatográficos_estabilidad_solucion_fase_movil: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Estabilidad de la fase móvil")

    # Robustez
    dir_reporte_lims_robustez: List[str] = Field(..., description="Directorio del reporte LIMS de Robustez del método")
    dirs_hoja_trabajo_robustez: List[str] = Field(..., description="Directorios de las Hojas de Trabajo de Preparación y Reporte de Robustez")
    dirs_bitacoras_robustez: List[str] = Field(..., description="Directorios de las Bitacoras de Preparación y Reporte de Robustez")
    dirs_soportes_cromatográficos_robustez: List[str] = Field(..., description="Directorios de los Soportes Cromatográficos de Robustez")
    
    context_for_render: Annotated[List[SupervisorResearchValidationOutput], operator.add]
    fname_out: str = Field(..., description="Nombre del archivo de salida")
    