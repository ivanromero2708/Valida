from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from src.config.models.set_1 import criterios


# Variables auxiliares


class DatosExactitudStrOutput(BaseModel):
    nivel: str = Field(..., description="Nivel de concentración")
    recuperacion: float = Field(..., description="Recuperación en porcentaje")
    promedio: float = Field(..., description="Promedio en porcentaje")


class ActivoExactitudStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    exactitud_metodo: List[DatosExactitudStrOutput] = Field(..., min_length=1, description="Datos de exactitud del sistema")
    conclusion_exactitud: str = Field(..., description="Cumple o No cumple con el criterio global")
    criterio_exactitud: str = Field(..., description="Criterio de exactitud")


class DatosExactitudStrExt(BaseModel):
    nivel: str = Field(..., description="Nivel de concentración")
    recuperacion: float =Field(..., description="Recuperación en porcentaje")


class ActivoExactitudStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    exactitud_metodo: List[DatosExactitudStrExt] = Field(..., min_length=1, description="Datos de exactitud del sistema")
    conclusion_exactitud: str = Field(..., description="Cumple o No cumple con el criterio global")
    criterio_exactitud: str = Field(..., description="Criterio de exactitud")


class Set4ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 4"""

    activos_exactitud: List[ActivoExactitudStrExt] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de exactitud para cada uno de los ingredientes activos del método")


# Modelos de validación de datos


class Set4RenderingModel(BaseModel):
    """Modelo de validación de datos del Set 4"""

    activos_exactitud: List[ActivoExactitudStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de exactitud para cada uno de los ingredientes activos del método")


class Set4StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 4"""

    activos_exactitud: List[ActivoExactitudStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de exactitud para cada uno de los ingredientes activos del método")
    referencia_exactitud: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de exactitud")
