from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from src.config.models.set_1 import criterios

# Variables auxiliares

class DatosPrecisionSistemaStrOutput(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del sistema")
    area_activo: float = Field(..., ge=0, le=200, description="Area bajo la curva del pico del activao validado")

class ActivoPrecisionSistemaStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_sistema: List[DatosPrecisionSistemaStrOutput] = Field(..., min_length=1, description="Datos de los valores obtenidos de las repliccas evaluadas en el parametro de precision del sistema")
    conclusion_precision_sistema: str = Field(..., description="Cumple o No cumple con el criterio global")
    criterio_precision_sistema: List[criterios] = Field(..., description="Criterios de aceptacion para precision del sistema")
    rsd_precision_sistema: float = Field(..., ge=0, le=200, description="RSD de los valores obtenidos de las repliccas evaluadas en el parametro de precision del sistema")
    
class DatosPrecisionSistemaStrExt(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del sistema")
    area_activo: float = Field(..., ge=0, le=200, description="Area bajo la curva del pico del activao validado")

class ActivoPrecisionsistemaStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_sistema: List[DatosPrecisionSistemaStrExt] = Field(..., min_length=1, description="Datos de los valores obtenidos de las repliccas evaluadas en el parametro de precision del sistema")
    conclusion_precision_sistema: str = Field(..., description="Cumple o No cumple con el criterio global")
    rsd_precision_sistema: float = Field(..., ge=0, le=200, description="RSD de los valores obtenidos de las repliccas evaluadas en el parametro de precision del sistema")
    criterio_precision_sistema: List[criterios] = Field(..., description="Criterios de aceptacion para precision del sistema")

class Set5ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 5"""

    activos_precision_sistema: List[ActivoPrecisionsistemaStrExt] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del sistema para cada uno de los ingredientes activos del método",)

# Modelos de validación de datos

class Set5RenderingModel(BaseModel):
    """Modelo de validación de datos del Set 5"""

    activos_precision_sistema: List[ActivoPrecisionSistemaStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del sistema para cada uno de los ingredientes activos del método",)
    referencia_precision_sistema: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de precision del sistema")

class Set5StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 5"""

    activos_precision_sistema: List[ActivoPrecisionSistemaStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del sistema para cada uno de los ingredientes activos del método",)
    referencia_precision_sistema: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de precision del sistema")
