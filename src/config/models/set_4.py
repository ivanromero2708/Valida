from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# Variables auxiliares

class DatosExactitudStrOutput(BaseModel):
    nivel: str = Field(..., description="Nivel de concentración")
    recuperacion: float = Field(..., ge=0, le=200, description="Recuperación en porcentaje")
    promedio: float = Field(..., ge=0, le=200, description="Promedio en porcentaje")

class ActivoExactitudStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    exactitud_sistema: List[DatosExactitudStrOutput] = Field(..., min_length=1, description="Datos de exactitud del sistema")
    conclusion: str = Field(..., description="Cumple o No cumple con el criterio global")

class DatosExactitudStrExt(BaseModel):
    nivel: str = Field(..., description="Nivel de concentración")
    recuperacion: float = Field(..., ge=0, le=200, description="Recuperación en porcentaje")

class ActivoExactitudStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    exactitud_sistema: List[DatosExactitudStrExt] = Field(..., min_length=1, description="Datos de exactitud del sistema")
    conclusion: str = Field(..., description="Cumple o No cumple con el criterio global")

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
    referencia_exactitud: str = Field(..., description="Referencia analítica")
