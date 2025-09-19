from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from src.config.models.set_1 import criterios


# Variables auxiliares

class DatosPrecisionMetodoStrOutput(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_activo: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")
   
class ActivoPrecisionMetodoStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_metodo: List[DatosPrecisionMetodoStrOutput] = Field(..., min_length=1, description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    conclusion_precision_metodo: str = Field(..., description="Cumple o No cumple con el criterio global")
    rsd_precision_metodo: float = Field(..., description="RSD de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    criterio_precision_metodo: List[criterios] = Field(..., description="Criterios de aceptacion para precision del metodo")

class DatosPrecisionMetodoStrExt(BaseModel):
    replica: str = Field(..., description="replica de la solucion evaluada en el parametro de precision del metodo")
    porcentaje_activo: float = Field(..., description="Porcentaje obtenido del activo evaluado en el parametro de precision del metodo")


class ActivoPrecisionMetodoStrExt(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    precision_metodo: List[DatosPrecisionMetodoStrExt] = Field(..., min_length=1, description="Datos de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    conclusion_precision_metodo: str = Field(..., description="Cumple o No cumple con el criterio global")
    rsd_precision_metodo: float = Field(..., description="RSD de los porcentajes obtenidos de las replicas evaluadas en el parametro de precision del metodo")
    criterio_precision_metodo: List[criterios] = Field(..., description="Criterios de aceptacion para precision del metodo")


class Set6ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 6"""

    activos_precision_metodo: List[ActivoPrecisionMetodoStrExt] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del metodo para cada uno de los ingredientes activos del método",)


# Modelos de validación de datos


class Set6RenderingModel(BaseModel):
    """Modelo de validación de datos del Set 6"""

    activos_precision_metodo: List[ActivoPrecisionMetodoStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del metodo para cada uno de los ingredientes activos del método",)
    referencia_precision_metodo: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de precision del metodo")

class Set6StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 6"""

    activos_precision_metodo: List[ActivoPrecisionMetodoStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de precision del metodo para cada uno de los ingredientes activos del método",)
    referencia_precision_metodo: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de precision del metodo")

