from pydantic import BaseModel, Field
from typing import List

## Variables auxiliares
class DataFactoresExperimentos(BaseModel):
    nombre_experimento: str = Field(..., description="Nombre del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la primera columna nombrsda como No. Experimentos.")
    temperatura: float = Field(..., description="Temperatura del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Temperatura (°C).")
    flujo: float = Field(..., description="Flujo del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Flujo (ml/min).")    
    volumen_inyeccion: float = Field(..., description="Volumen de inyeccion del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Volumen de inyeccion (µL).") 
    fase_movil: str = Field(..., description="Fase movil del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Fase movil (Solucion amortiguadora: ACN).")    

    
class DataRobustezStrOutput(BaseModel):
    experimento: str = Field(..., description="nombre del experimento analítico donde se varia un factor para determoinar si existe variacion en los resultados del metodo analitico del parámetro de robustez, se reporta como Robustness Flow, Robustness Temperature, Robustness Inyection volume, Robustness Mobile phase")  
    replica: int = Field(..., description="Réplica del dato de robustez, se reporta para cada experimento analítico como Solucion Muestra Flujo Nominal 1, ... Solucion Muestra Flujo Nominal 3 para el experimento nominal, Solucion Muestra Flujo Bajo 1... Solucion Muestra Flujo Bajo 3, solucion muestra flujo alto 1... solucion muestra flujo alto 3, asi respectivamente para todos los demas experimentos.")
    valores_aproximados: float = Field(..., description="Valores aproximados obtenidos del activo evaluado en el parametro de robustez,se reportan para cada réplica del experimento analítico como porcentaje en la columna de cada experimento por ejemplo Robustness Flow, Robustness Temperature, Robustness Inyection volume, Robustness Mobile phase")    
    promedio_experimento: float = Field(..., description="Promedio de los valores aproximados obtenidos del activo evaluado en el parametro de robustez, se reporta como promedio del experimento analítico por ejemplo Promedio Temperatura nominal, Promedio temperatura Baja, Promedio temperatura Alta, Promedio Flujo Nominal, Promedio Flujo Bajo, Promedio Flujo Alto....")
    diferencia_porcentaje: float = Field(..., description="Diferencia de los porcentajes obtenidos del activo evaluado en cda experimento en el parametro de robustez con respecto al valor obtenido en el experimento nominal, se reporta como %di Flujo Bajo, %di Flujo Alto, %di Temperatura Baja, %di Temperatura Alta, %di Volumen de inyeccion Bajo, %di Volumen de inyeccion Alto.")    
    

class ActivoRobustezStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo")
    robustez: List[DataRobustezStrOutput] = Field(..., min_length=1, description="Datos de los porcentajes obtenidos de las replicas evaluadas en los experimentos del parametro de robustez")
    conclusion_robustez: str = Field(..., description="Cumple o No cumple con el criterio de aceptacion para el parametro de validacion de robustez")
    criterio_robustez: str = Field(..., description="Criterios de aceptacion para el parametro de validacion de robustez")

# Modelos de validación de datos

class Set11ExtractionModel(BaseModel):
    """Modelo de validación de datos del Set 11"""
    activos_robustez: List[ActivoRobustezStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de robustez para cada uno de los ingredientes activos del método",)
    referencia_robustez: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de robustez")
    experimento_robustez: List[DataFactoresExperimentos]= Field(..., description="Experimento analítico del reporte de los resultados del parámetro de robustez") 

class Set11StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 11"""
    activos_robustez: List[ActivoRobustezStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de robustez para cada uno de los ingredientes activos del método",)
    referencia_robustez: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de robustez")
    experimentos_robustez: List[DataFactoresExperimentos] = Field(..., description="Factores que se modifican para verificar si existe variacion en los resultados del metodo analitico y comprobar si es robusto.") 