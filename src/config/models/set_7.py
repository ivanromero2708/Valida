from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# Variables auxiliares

class DatosPrecisionIntermediaStrExt(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_an1: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    porcentaje_an2: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    
class ActivoPrecisionIntermediaStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_intermedia: List[DatosPrecisionIntermediaStrExt] = Field(..., description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    rsd_analista: float = Field(..., description="RSD de los porcentajes obtenidos del activo evaluado realizado por el analista")
    criterio_precision_intermedia: str = Field(..., description="Criterios de aceptacion para precision intermedia")

class DatosPrecisionIntermediaStrOutput(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_an1: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    porcentaje_an2: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
    
class ActivoPrecisionIntermediaStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_intermedia: List[DatosPrecisionIntermediaStrOutput] = Field(..., description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    rsd_an1_an2: float = Field(..., description="RSD de los porcentajes obtenidos del activo evaluado entre analistas")
    criterio_precision_intermedia: str = Field(..., description="Criterios de aceptacion para precision intermedia")
    promedio_an1: float = Field(..., description="Promedio de los porcentajes obtenidos del activo evaluado realizado por el analista 1")
    promedio_an2: float = Field(..., description="Promedio de los porcentajes obtenidos del activo evaluado realizado por el analista 2")
    diferencia_promedio_an1_an2: float = Field(..., description="Diferencia de los porcentajes obtenidos del activo evaluado realizado por el analista 1 y el analista 2")

# Modelos de validación de datos

class Set7ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 7"""

    activos_precision_intermedia: List[ActivoPrecisionIntermediaStrExt] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision intermedia para cada uno de los ingredientes activos del método",)


class Set7StructuredOutputSupervisor(BaseModel):
    """Modelo de  validación de datos del Set 7"""

    activos_precision_intermedia: List[ActivoPrecisionIntermediaStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision intermedia para cada uno de los ingredientes activos del método",)
    referencia_precision_intermedia: str = Field(..., description="Referencia analítica reportada en el reporte de los resultados del parámetro de precision intermedia")
