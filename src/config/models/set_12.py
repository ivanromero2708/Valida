from pydantic import BaseModel, Field
from typing import List, Literal

## Modelos de extraccion de datos

class DatoReplicas(BaseModel):
    replica: int = Field(..., description="Réplica del dato de robustez, se reporta para cada experimento analítico como Solucion Muestra Flujo Nominal 1, ... Solucion Muestra Flujo Nominal 3 para el experimento nominal, Solucion Muestra Flujo Bajo 1... Solucion Muestra Flujo Bajo 3, solucion muestra flujo alto 1... solucion muestra flujo alto 3, asi respectivamente para todos los demas experimentos.")
    valor: float = Field(..., description="Valor del dato de robustez, se reporta para cada réplica del experimento analítico como porcentaje en la columna de cada experimento por ejemplo Robustness Flow, Robustness Temperature, Robustness Inyection volume, Robustness Mobile phase")

class DataRobustez(BaseModel):
    nombre_analito: str = Field(..., description="Nombre del ingrediente activo, impureza, o producto de degradación")
    variable_entrada: str = Field(..., description="Variable a evaluar durante la prueba de validación de robustez.. Se encuentra en las tablas de datos cerca de la clave 'Robustness'")
    promedio_nominal: float = Field(..., description="Promedio de los valores evaluados en la condición nominal de la variable de entrada. Se encuentra cerca de las claves 'Promedio' y 'nominal'")
    promedio_bajo: float = Field(..., description="Promedio de los valores evaluados en la condición Bajo de la variable de entrada. Se encuentra cerca de las claves 'Promedio' y 'Bajo'")
    promedio_alto: float = Field(..., description="Promedio de los valores evaluados en la condición Alto de la variable de entrada. Se encuentra cerca de las claves 'Promedio' y 'Alto'")
    di_porcentaje_bajo: float = Field(..., description="Valores del %di en el nivel alto de la variables de entrada. Se encuentra cerca las claves '%di' y 'Bajo'")
    di_porcentaje_alto: float = Field(..., description="Valores del %di en el nivel alto de la variables de entrada. Se encuentra cerca las claves '%di' y 'Alto'")
    replicas_nominal: List[DatoReplicas] = Field(..., description="Listado de valores de las réplicas del porcentaje al nivel nominal. Se encuentra cerca de las claves 'Solucion muestra' y 'nominal'")
    replicas_bajo: List[DatoReplicas] = Field(..., description="Listado de valores de las réplicas del porcentaje al nivel bajo. Se encuentra cerca de las claves 'Solucion muestra' y 'bajo'")
    replicas_alto: List[DatoReplicas] = Field(..., description="Listado de valores de las réplicas del porcentaje al nivel alto. Se encuentra cerca de las claves 'Solucion muestra' y 'alto'")

class Set12ExtractionModel(BaseModel):
    data_robustez: List[DataRobustez] = Field(..., description="Datos de los porcentajes, promedios y diferencias obtenidos de las replicas evaluadas en los experimentos del parametro de robustez")

## Modelos de impresión de reporte

class DataRobustezStrOutput(BaseModel):
    experimento: str = Field(..., description="nombre del experimento analítico donde se varia un factor para determoinar si existe variacion en los resultados del metodo analitico del parámetro de robustez, se reporta como Robustez Flujo Alto, Robustez Flujo Bajo, Robustez Temperatura Alto, entre otros..")  
    replica: int = Field(..., description="Réplica del dato de robustez, se reporta para cada experimento analítico como Solucion Muestra Flujo Nominal 1, ... Solucion Muestra Flujo Nominal 3 para el experimento nominal, Solucion Muestra Flujo Bajo 1... Solucion Muestra Flujo Bajo 3, solucion muestra flujo alto 1... solucion muestra flujo alto 3, asi respectivamente para todos los demas experimentos.")
    valores_aproximados: float = Field(..., description="Valores aproximados obtenidos del activo evaluado en el parametro de robustez,se reportan para cada réplica del experimento analítico como porcentaje en la columna de cada experimento por ejemplo Robustness Flow, Robustness Temperature, Robustness Inyection volume, Robustness Mobile phase")    
    promedio_experimento: float = Field(..., description="Promedio de los valores aproximados obtenidos del activo evaluado en el parametro de robustez, se reporta como promedio del experimento analítico por ejemplo Promedio Temperatura nominal, Promedio temperatura Baja, Promedio temperatura Alta, Promedio Flujo Nominal, Promedio Flujo Bajo, Promedio Flujo Alto....")
    diferencia_porcentaje: float = Field(..., description="Diferencia de los porcentajes obtenidos del activo evaluado en cda experimento en el parametro de robustez con respecto al valor obtenido en el experimento nominal, se reporta como %di Flujo Bajo, %di Flujo Alto, %di Temperatura Baja, %di Temperatura Alta, %di Volumen de inyeccion Bajo, %di Volumen de inyeccion Alto.")    

class ActivoRobustezStrOutput(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo, impureza, o producto de degradación")
    robustez: List[DataRobustezStrOutput] = Field(..., description="Datos de los porcentajes obtenidos de las replicas evaluadas en los experimentos del parametro de robustez")
    conclusion_robustez: str = Field(..., description="Cumple o No cumple con el criterio de aceptacion para el parametro de validacion de robustez")
    criterio_robustez: str = Field(..., description="Criterios de aceptacion para el parametro de validacion de robustez")

# Modelos de validación de datos
class Set12StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos del Set 12"""
    activos_robustez: List[ActivoRobustezStrOutput] = Field(..., description="Listado de diccionarios que contiene toda la información relacionada con la validación del parámetro de robustez para cada uno de los ingredientes activos del método",)
    referencia_robustez: str = Field(..., description="Referencia analítica del reporte de los resultados del parámetro de robustez")