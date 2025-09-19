from pydantic import BaseModel, Field
from typing import List, Optional

# Variables auxiliares

class DataFaseMovilTiempo(BaseModel):
    replica: int = Field(..., description="Réplica del dato de validación de la fase movil, es un entero que inicia en 1 hacia adelante, se encuentra reportada en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como replica.")
    areas_system: float = Field(..., description="Área bajo la curva del pico asociado al dato de validación de la fase movil, se encuentra reportada en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Area.")
    tiempo_retencion: float = Field(..., description="Tiempo de retención del ingrediente activo, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como tiempo de retención.")
    usp_tailing: float = Field(..., description="USP Tailing del ingrediente activo, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como USP tailing.")
    resolucion: float = Field(..., description="Resolución entre los picos de los ingredientes activos, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Resolución.")
    exactitud: float = Field(..., description="factor de Exactitud de las areas del ingrediente activo, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Exactitud.")

class DataFaseMovilTiempos(BaseModel):
    tiempo: str = Field(..., description="Tiempo de validacion de la fase movil, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Estabilidad Fase Movil Tiempo  inicial, Estabilidad Fase Movil Tiempo 1, Estabilidad Fase Movil Tiempo 2.")
    promedio_areas_system: float = Field(..., description="Promedio de las areas del sistema, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Promedio Areas o con una x barra.")
    promedio_tiempo_retencion: float = Field(..., description="Promedio de tiempo de retencion, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Promedio Tiempo Retention o con una x barra.")
    promedio_usp_tailing: float = Field(..., description="Promedio de usp tailing, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Promedio USP Tailing o con una x barra.")
    promedio_resolucion: float = Field(..., description="Promedio de resolucion, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como Promedio Resolucion o con una x barra.")
    rsd_areas_system: float = Field(..., description="RSD de las areas del sistema, se encuentra reportado en la hoja de trabajo de analisis fisico quimico complementario en la seccion DESARROLLO DEL PROCEDIMIENTO, como %RSD o %rsd.")
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
    activos_fase_movil: List[EstabilidadFaseMovil] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de estabilidad de la fase movil para cada uno de los ingredientes activos del método")
    referencia_estabilidad_fase_movil: str= Field(..., description="Referencia analítica del reporte de resultaods de estabilidad de la fase movil")


class Set10StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos para Salida estructurada Estabilidad de la fase movil"""
    activos_fase_movil: List[EstabilidadFaseMovil] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de estabilidad de la fase movil para cada uno de los ingredientes activos del método")
    referencia_estabilidad_fase_movil: str= Field(..., description="Referencia analítica del reporte de resultaods de estabilidad de la fase movil")
