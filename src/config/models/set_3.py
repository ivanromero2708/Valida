from pydantic import BaseModel, Field
from typing import List, Literal
from src.config.models.set_1 import criterios

# Variables auxiliares
class LinealidadSistema(BaseModel):
    nivel: str = Field(..., description = "Nivel de concentración de la muestra usada para la validación de linealidad. Se reporta de esta manera (Pueden haber más valores, no necesariamente son estos): I (50%), II (75%), III (100%), IV (125%), V (150%)")
    concentracion: float = Field(..., description = "Concentración de la muestra en mg/mL. Son 3 réplicas, aqui vas a ir reportando cada una de las réplicas")
    area_pico: float = Field(..., description = "Área del pico reportada por cada réplica")
    factor_respuesta: float = Field(..., description= "Factor de respuesta por cada réplica")


class ParametroLinealidad(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo con la data de validación de linealidad")
    linealidad_sistema: List[LinealidadSistema] = Field(..., description="Datos de linealidad del sistema")
    rsd_factor: float = Field(..., description="RSD de los factores de respuesta")
    pendiente: float = Field(..., description="Pendiente de la curva (b)")
    intercepto: float = Field(..., description="Intercepto (a)")
    r: float = Field(..., description="Coeficiente de correlación (r)")
    r2: float = Field(..., description="Coeficiente de Determinación (r2)")
    porcentaje_intercepto: float = Field(..., description="Intercepto como porcentaje de 0 al 100%")
    cumple_global: Literal["Cumple", "No Cumple"] = Field(..., description="Cumple con el criterio global")
    criterio_linealidad: List[criterios] = Field(..., description="Criterios de aceptacion para linealidad linealidad")
   

class LinealidadSistemaExtraccion(LinealidadSistema):
    nivel: str = Field(..., description = "Nivel de concentración de la muestra usada para la validación de linealidad. Se reporta de esta manera (Pueden haber más valores, no necesariamente son estos): Solucion Linealidad Nivel 1 R1, Solucion Linealidad Nivel 2 R2, Solucion Linealidad Nivel 3 R3, Solucion Linealidad Nivel 2 R1, Solucion Linealidad Nivel 2 R2, Solucion Linealidad Nivel 2 R3....")
    concentracion: float = Field(..., description = "Concentración de la muestra en mg/mL. Se reporta en la columna de Concentration")
    area_pico: float = Field(..., description = "Área del pico reportada por cada réplica. Se reporta en la columna de Response")
    factor_respuesta: float = Field(..., description= "Factor de respuesta por cada réplica. Se reporta en la columna de Response factor")

class ParametroLinealidadExtraccion(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo con la data de validación de linealidad")
    linealidad_sistema: List[LinealidadSistemaExtraccion] = Field(..., description="Datos de linealidad del sistema")
    rsd_factor: float = Field(..., description="RSD de los Factores de Respuesta (Reportado como RSD Response Factor)")
    pendiente: float = Field(..., description="Pendiente de la curva (b) (Reportado como Slope)")
    intercepto: float = Field(..., description="Intercepto (a) (Reportado como Intercept)")
    r: float = Field(..., description="Coeficiente de correlación (r) (Reportado como Correlation coefficient (r))")
    r2: float = Field(..., description="Coeficiente de Determinación (r2) (Reportado como Determination coefficient (r2))")
    porcentaje_intercepto: float = Field(..., description="Intercepto como porcentaje de 0 al 100% (Reportado como Intercepto as percentage of Y at 100%)")
    cumple_global: Literal["Cumple", "No Cumple"] = Field(..., description="Cumple con el criterio global")
    criterio_linealidad: List[criterios] = Field(..., description="Criterios de aceptacion para linealidad linealidad")


#Modelos de validación de datos



class Set3ExtractionModel(BaseModel):
    """Modelo de validación de datos Set 3"""
    activos_linealidad: List[ParametroLinealidadExtraccion] = Field(..., description="Lista de diccionarios que contiene toda la información de validación del parámetro de linealidad para un API específico. Esta información se extrae del reporte LIMS. Si hay varios ingredientes activos en el producto, hay varios elementos de activos_linealidad. Incluye los resultados de linealidad (reportados en forma tabular con las columnas Level, Concentration, Response, y Response factor), RSD de los Factores de Respuesta (Reportado como RSD Response Factor), Pendiente de la curva (b) (Reportado como Slope), Intercepto (a) (Reportado como Intercept), Coeficiente de correlación (r) (Reportado como Correlation coefficient (r)), Coeficiente de Determinación (r2) (Reportado como Determination coefficient (r2)), Intercepto como porcentaje de y ̂al 100% (Reportado como Intercepto as percentage of Y at 100%)")

class Set3RenderingModel(BaseModel):
    """Modelo de validación de datos Set 3"""
    activos_linealidad: List[ParametroLinealidad] = Field(..., description="Lista de diccionarios que contiene toda la información de validación del parámetro de linealidad para un API específico. Si hay varios ingredientes activos en el producto, hay varios elementos de activos_linealidad. Incluye los resultados de linealidad, RSD de los Factores de Respuesta, Pendiente de la curva (b), Intercepto (a), Coeficiente de correlación (r), Coeficiente de Determinación (r2), Intercepto como porcentaje de y ̂ al 100%, Criterio de aceptación , y Conclusión por cada Ingrediente activo")
    referencia_linealidad: str = Field(..., description="Código del documento donde se encuentra consignados los valores brutos de esta tabla. Puede ser un reporte LIMS, una hoja de trabajo o una bitácora")
    
class Set3StructuredOutputSupervisor(BaseModel):
    """Modelo de validación de datos Set 3"""
    activos_linealidad: List[ParametroLinealidad] = Field(..., description="Lista de diccionarios que contiene toda la información de validación del parámetro de linealidad para un API específico. Si hay varios ingredientes activos en el producto, hay varios elementos de activos_linealidad. Incluye los resultados de linealidad, RSD de los Factores de Respuesta, Pendiente de la curva (b), Intercepto (a), Coeficiente de correlación (r), Coeficiente de Determinación (r2), Intercepto como porcentaje de y ̂ al 100%, Criterio de aceptación , y Conclusión por cada Ingrediente activo")
    referencia_linealidad: str = Field(..., description="Código del documento donde se encuentra consignados los valores brutos de esta tabla. Puede ser un reporte LIMS, una hoja de trabajo o una bitácora")
