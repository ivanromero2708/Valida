from pydantic import BaseModel, Field
from typing import List

## Variables auxiliares
class DataFactoresExperimentos(BaseModel):
    nombre_experimento: str = Field(..., description="Nombre del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la primera columna nombrada como No. Experimentos.")
    temperatura: float = Field(..., description="Temperatura del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Temperatura (°C).")
    flujo: float = Field(..., description="Flujo del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Flujo (ml/min).")    
    volumen_inyeccion: float = Field(..., description="Volumen de inyeccion del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Volumen de inyeccion (µL).") 
    fase_movil: str = Field(..., description="Fase movil del experimento analítico, se reporta en el protocolo de validacion en la tabla descrita como condiciones de robustez ubicada en la columna nombrada como Fase movil (Solucion amortiguadora: ACN).")    
    
# Modelos de validación de datos

class Set11ExtractionModel(BaseModel):
    experimento_robustez: List[DataFactoresExperimentos]= Field(..., description="Experimento analítico del reporte de los resultados del parámetro de robustez. SOLO VAS A EXTRAER ESTOS DATOS DE LA TABLA CON LA CLAVE 'Condiciones de robustez' o similar") 

class Set11StructuredOutputSupervisor(BaseModel):
    experimentos_robustez: List[DataFactoresExperimentos] = Field(..., description="Factores que se modifican para verificar si existe variacion en los resultados del metodo analitico y comprobar si es robusto.") 