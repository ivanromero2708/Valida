from pydantic import BaseModel, Field
from typing import List
from datetime import date
from typing import Literal

# Protocolo de validación
class CriterioValidacion(BaseModel):
    parametro: Literal["Linealidad", "Exactitud del método (Recuperación)", "Precisión del sistema", "Precisión del método (´Repetibilidad)", "Precisión intermedia", "Precisión del método (Reproducibilidad)", "Rango (Intervalo)", "Robustez del método", "Estabilidad analítica de las soluciones", "Estabilidad analítica de la fase móvil"] = Field(..., description="Nombre del parametro de validación")
    criterio_aceptacion: str = Field(..., description="Descripción de texto del criterio de aceptación del parámetro en el protocolo de validación")

# Variables auxiliares

class DataReplicaEstabilidadSoluciones(BaseModel):
    replica: int = Field(..., description="Réplica del dato de estabilidad de las soluciones, es un entero que inicia en 1 hacia adelante, se encuentra reportado como Solucion Muestra o Estandar R1, Solucion Muestra o Estandar R2, Solucion Muestra o Estandar R3 para cada condicion 1 y 2 y cada tiempo de estabilidad")
    area: float = Field(..., description="Área bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportados en las columnas de los difrentes tiempos de estabilidad Initial Sample Stability, Sample Stability Time 1... como Results asociados con cada Solucion Muestra o Estandar R1 .. de cada condicion 1 y 2")

class DataEstabilidadSoluciones(BaseModel):
    """Modelo de validación de datos de la estabilidad de las soluciones"""
    analito: str = Field(..., description="Nombre del analito que puede ser un ingrediente activo farmacéutico, una impureza, un producto de degradación, en general un analito de estudio de la validación")
    condicion_estabilidad: str = Field(..., description="Condición de almacenamiento de las soluciones para validación de su estabilidad, reportada para cada tiempo de estabilidad como Tiempo inicial, Condicion 1, Condición 2, Condicion 3, etc.")
    tiempo_estabilidad: str = Field(..., description="Tiempo de estabilidad de las soluciones, reportado como (Initial Sample Stability) para tiempo 0, Sample Stability Time 1 para el primer tiempo y Sample Stability Time n para los demás tiempos del reporte LIMS para estabilidad")
    promedio_areas: float = Field(..., description="Promedio de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportado como Promedio Solucion Muestra Tiempo Inicial, Promedio Solucion Muestra Tiempo 1 condicion 1, Promedio Solucion Muestra Tiempo 1 condicion 2, Promedio Solucion Muestra Tiempo 2 condicion 1, Promedio Solucion Muestra Tiempo 2 condicion 2......")
    diferencia_promedios: float = Field(..., description="Diferencia entre los promedios de las áreas bajo la curva del pico asociado al dato de validación de la estabilidad de las soluciones, reportado como %di Solucion Muestra Tiempo 1 condicion 1, %di Solucion Muestra Tiempo 1 condicion 2, %di Solucion Muestra Tiempo 2 condicion 1, %di Solucion Muestra Tiempo 2 condicion 2......")
    data_condicion: list[DataReplicaEstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.")
    referencia_analitica: str = Field(..., description="Lista de referencias analíticas de la solucion")

class EstabilidadSoluciones(BaseModel):
    solucion: str = Field(..., description="Nombre de la solucion que puede ser Solucion Estandar o Solucion Muestra acompañado del nombre del analito")
    tipo_solucion: Literal["Solucion_Estandar", "Solucion_Muestra"] = Field(..., description="Tipo de solucion que puede ser Solucion Estandar o Solucion Muestra")
    data_estabilidad_solucion: List[DataEstabilidadSoluciones]= Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de la solucion identificada.",)
    criterios_validacion: List[CriterioValidacion] = Field(..., description="Lista de criterios de aceptación de las pruebas de validación presentes en el protocolo de validación")

# Modelos de validación de datos

class Set8ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 9"""
    activos_estabilidad_solucion: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica_estabilidad_soluciones: str = Field(..., description="Lista de las referencias analíticas de las soluciones estandar y muestra")

class Set8StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 9"""
    activos_estabilidad_solucion: List[EstabilidadSoluciones] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la estabilidad de las soluciones de estandares y muestras.",)
    referencia_analitica_estabilidad_soluciones: str = Field(..., description="Lista de las referencias analíticas identificadas para la solución")
    conclusion_estabilidad_soluciones: str = Field(..., description="Conclusion de la estabilidad de las soluciones")
