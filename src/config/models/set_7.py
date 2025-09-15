from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from src.config.models.set_1 import criterios

# Variables auxiliares

class PromedioAnalistas(BaseModel):
    promedio_an1: float = Field(..., ge=0, le=200, description="Promedio de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision intermedia para el analista 1")
    promedio_an2: float = Field(..., ge=0, le=200, description="Promedio de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision intermedia para el analista 2")

class DatosPrecisionIntermediaStrOutput(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_an1: float = Field(..., ge=0, le=200, description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    porcentaje_an2: float = Field(..., ge=0, le=200, description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    promedio_analistas: List[PromedioAnalistas] = Field(..., ge=0, le=200, description="Promedio de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision intermedia")
    

class ActivoPrecisionIntermediaStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_intermedia: List[DatosPrecisionIntermediaStrOutput] = Field(..., min_length=1, description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    conclusion: str = Field(..., description="Cumple o No cumple con el criterio global")
    rsd_an1_an2: float = Field(..., ge=0, le=200, description="RSD de los porcentajes obtenidos del activo evaluado en el parametro de precision del metodo")
    diferencia_promedio_an1_an2: float = Field(..., ge=0, le=200, description="Diferencia de los porcentajes obtenidos del activo evaluado en el parametro de precision del metodo")
    criterio_precision_intermedia: List[criterios] = Field(..., description="Criterios de aceptacion para precision intermedia")

class DatosPrecisionIntermediaStrExt(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_an1: float = Field(..., ge=0, le=200, description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    porcentaje_an2: float = Field(..., ge=0, le=200, description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    
class ActivoPrecisionIntermediaStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_intermedia: List[DatosPrecisionIntermediaStrExt] = Field(..., min_length=1, description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    conclusion: str = Field(..., description="Cumple o No cumple con el criterio global")
    rsd_an1_an2: float = Field(..., ge=0, le=200, description="RSD de los porcentajes obtenidos del activo evaluado en el parametro de precision del metodo")
    diferencia_promedio_an1_an2: float = Field(..., ge=0, le=200, description="Diferencia de los porcentajes obtenidos del activo evaluado en el parametro de precision del metodo")
    criterio_precision_intermedia: List[criterios] = Field(..., description="Criterios de aceptacion para precision intermedia")

class Set7ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 7"""

    activos_precision_intermedia: List[ActivoPrecisionIntermediaStrExt] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision intermedia para cada uno de los ingredientes activos del método",)


# Modelos de validación de datos


class Set7RenderingModel(BaseModel):
    """Modelo de validación de datos del Set 7"""

    activos_precision_intermedia: List[ActivoPrecisionIntermediaStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision intermedia para cada uno de los ingredientes activos del método",)
    referencia_precision_intermedia: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de precision intermedia")

class Set7StructuredOutputSupervisor(BaseModel):
    """Modelo de  validación de datos del Set 7"""

    activos_precision_intermedia: List[ActivoPrecisionIntermediaStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision intermedia para cada uno de los ingredientes activos del método",)
    referencia_precision_intermedia: str = Field(..., description="Referencia analítica reportada en el reporte de los resultados del parámetro de precision intermedia")
