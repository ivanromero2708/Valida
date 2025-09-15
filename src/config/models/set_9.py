from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# Variables auxiliares

class DataReplicaEstabilidadSoluciones(BaseModel):
    replica: int = Field(..., description="Réplica del dato de estabilidad de las soluciones, es un entero que inicia en 1 hacia adelante.")
    area: float = Field(..., description="Área bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones")

class DataEstabilidadSoluciones(BaseModel):
    """Modelo de validación de datos de la estabilidad de las soluciones"""    
    condicion_estabilidad: str = Field(..., description="Condición de almacenamiento de las soluciones para validación de su estabilidad")
    tiempo_estabilidad: str = Field(..., description="Tiempo de estabilidad de las soluciones")
    promedio_areas: float = Field(..., description="Promedio de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones")
    diferencia_promedios: float = Field(..., description="Diferencia entre los promedios de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones")
    criterio_aceptacion: str = Field(..., description="Criterio de aceptación para la estabilidad de las soluciones")
    conclusion_estabilidad: str = Field(..., description="Conclusion de la estabilidad de las soluciones")
    data_condicion: list[DataReplicaEstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)

class EstabilidadSoluciones(BaseModel):
    solucion: str = Field(..., description="Nombre de la solucion estandar o muestra")
    data_estabilidad_solucion: List[DataEstabilidadSoluciones]

# Modelos de validación de datos

class Set9ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 9"""
    soluciones: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica: List[str] = Field(..., description="Referencia analítica de las soluciones estandar y muestra")

class Set9StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 8"""
    soluciones: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica: List[str] = Field(..., description="Referencia analítica de las soluciones estandar y muestra")
