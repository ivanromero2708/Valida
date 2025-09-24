from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# Variables auxiliares

class DataReplicaEstabilidadSoluciones(BaseModel):
    replica: int = Field(..., description="Réplica del dato de estabilidad de las soluciones, es un entero que inicia en 1 hacia adelante, se encuentra reportado como Solucion Muestra R1, Solucion Muestra R2, Solucion Muestra R3 para cada condicion 1 y 2 y cada tiempo de estabilidad")
    area: float = Field(..., description="Área bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportados en las columnas de los difrentes tiempos de estabilidad Initial Sample Stability, Sample Stability Time 1... como Results asociados con cada Solucion Muestra R1 .. de cada condicion 1 y 2")

class DataEstabilidadSoluciones(BaseModel):
    """Modelo de validación de datos de la estabilidad de las soluciones"""    
    condicion_estabilidad: str = Field(..., description="Condición de almacenamiento de las soluciones para validación de su estabilidad, reportada para cada tiempo de estabilidad como Solucion Muestra R1 Condicion 1, Solucion Muestra R2 Condicion 1, Solucion Muestra R3 Condicion 1, Solucion Muestra R1 Condicion 2, Solucion Muestra R2 Condicion 2, Solucion Muestra R3 Condicion 2, para cada uno de los tiempos evaluados.")
    tiempo_estabilidad: str = Field(..., description="Tiempo de estabilidad de las soluciones, reportado como (Initial Sample Stability) para tiempo 0, Sample Stability Time 1 para el primer tiempo y Sample Stability Time n para los demás tiempos del reporte LIMS para estabilidad")
    promedio_areas: float = Field(..., description="Promedio de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportado como Promedio Solucion Muestra Tiempo Inicial, Promedio Solucion Muestra Tiempo 1 condicion 1, Promedio Solucion Muestra Tiempo 1 condicion 2, Promedio Solucion Muestra Tiempo 2 condicion 1, Promedio Solucion Muestra Tiempo 2 condicion 2......")
    diferencia_promedios: float = Field(..., description="Diferencia entre los promedios de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportado como %di Solucion Muestra Tiempo 1 condicion 1, %di Solucion Muestra Tiempo 1 condicion 2, %di Solucion Muestra Tiempo 2 condicion 1, %di Solucion Muestra Tiempo 2 condicion 2......")
    conclusion_estabilidad: str = Field(..., description="Conclusion de la estabilidad de las soluciones")
    data_condicion: list[DataReplicaEstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)

class EstabilidadSoluciones(BaseModel):
    solucion: str = Field(..., description="Nombre de la solucion estandar o muestra")
    data_estabilidad_solucion: List[DataEstabilidadSoluciones]
    criterio_aceptacion: str = Field(..., description="Criterio de aceptación para la estabilidad de las soluciones")

# Modelos de validación de datos

class Set9ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 9"""
    activos_estabilidad_solucion_muestra: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica: List[str] = Field(..., description="Referencia analítica de las soluciones estandar y muestra")

class Set9StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 9"""
    activos_estabilidad_solucion_muestra: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica: List[str] = Field(..., description="Referencia analítica de las soluciones estandar y muestra")
    conclusion_estabilidad_muestra: str = Field(..., description="Conclusion de la estabilidad de las soluciones")
