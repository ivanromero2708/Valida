from pydantic import BaseModel, Field
from typing import List, Optional

# Variables auxiliares

class DataFaseMovilTiempo(BaseModel):
    replica: int = Field(..., description="Réplica del dato de validación de la fase movil, es un entero que inicia en 1 hacia adelante.")
    areas_system: float = Field(..., description="Área bajo la curva del pico asociado al dato de validación de la fase movil")
    tiempo_retencion: float = Field(..., description="Tiempo de retención del ingrediente activo")
    usp_tailing: float = Field(..., description="USP Tailing del ingrediente activo")

class DataFaseMovilTiempos(BaseModel):
    tiempo: str = Field(..., description="Tiempo de validacion de la fase movil")
    promedio_areas_system: float = Field(..., description="Promedio de las areas del sistema")
    promedio_tiempo_retencion: float = Field(..., description="Promedio de tiempo de retencion")
    promedio_usp_tailing: float = Field(..., description="Promedio de usp tailing")
    rsd_areas_system: float = Field(..., description="RSD de las areas del sistema")
    criterio_aceptacion: str = Field(..., description="Criterio de aceptacion para la fase movil")
    conclusion_areas_system: str = Field(..., description="Conclusion de areas system de la fase movil")
    conclusion_tiempo_retencion: str = Field(..., description="Conclusion de tiempo de retención de la fase movil")
    conclusion_usp_tailing: str = Field(..., description="Conclusion de usp tailing de la fase movil")
    data_fase_movil_tiempo: List[DataFaseMovilTiempo] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la fase movil.")

class EstabilidadFaseMovil(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo cuya fase movil esta siendo validada")
    data_fase_movil_tiempos: List[DataFaseMovilTiempos] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la fase movil.")

# Modelos de datos

class Set10ExtractionModel(BaseModel):
    """Modelo de validación de datos para Salida estructurada Estabilidad de la fase movil"""
    fases: List[EstabilidadFaseMovil]
    referencia_analitica: str


class Set10StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos para Salida estructurada Estabilidad de la fase movil"""
    fases: List[EstabilidadFaseMovil]
    referencia_analitica: str
