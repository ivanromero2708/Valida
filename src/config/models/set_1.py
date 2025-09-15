from pydantic import BaseModel, Field
from typing import List, Optional
 
# Set 1 - Plan de razonamiento
# - validacion: tipo str, obligatorio - nombre del informe
# - codigo_informe: tipo str, obligatorio - código del informe
# - nombre_producto: tipo str, obligatorio - nombre del producto farmacéutico
# - codigo_producto: tipo str, obligatorio - código del producto
# - lista_activos: tipo List[str], obligatorio - lista de activos
# - concentracion_activos: tipo str, obligatorio - concentración de activos
# - rango_validado: tipo str, obligatorio - rango validado
# - activos[]: Lista de objetos Activo con subcampo nombre
# - código_protocolo_validacion: tipo str, obligatorio - código del protocolo de validación
# - nombre_del_protocolo_validacion: tipo str, obligatorio - nombre del protocolo de validación
# - concentracion_activos: tipo str, obligatorio - concentración de activos
# - rango_validado: tipo str, obligatorio - rango validado
# - parámetros_de_validacion: tipo List[str], obligatorio - lista de parámetros de validación
 
class API(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo.")
    concentracion: str = Field(..., description="Concentración del ingrediente activo")

class parametros(BaseModel):
    nombre: str = Field(..., description="Nombre de cada parametro de validacion evaluado para el metodo analitico.")
    selectividad: str = Field(..., description="Capacidad de medir sin interferencias de matriz.")
    linealidad: str = Field(..., description="Proporcionalidad de respuesta con concentración.")
    exactitud: str = Field(..., description="Proximidad al valor verdadero (recuperación).")
    precision_sistema: str = Field(..., description="Repetibilidad del sistema de inyección/detección.")
    precision_metodo: str = Field(..., description="Repetibilidad de preparación y medida de muestras.")
    precision_intermedia: str = Field(..., description="Reproducibilidad intralaboratorio entre condiciones.")
    rango: str = Field(..., description="Límite inferior y superior validados.")
    estabilidad_soluciones: str  = Field(..., description="Constancia temporal de respuesta de soluciones.")
    estabilidad_fase_movil: str = Field(..., description="Estabilidad de fase móvil y su efecto en tiempos/áreas.")
    robustez: str = Field(..., description="Insensibilidad a pequeñas variaciones del método.")


class criterios(BaseModel):
   criterio_selectividad: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es ausencia aceptable de interferencias para el analito.")
   criterio_linealidad: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es cumplir con requisitos de r/r², pendiente, intercepto y residuale")
   criterio_exactitud: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es exactitud de rangos de recuperación aceptables por nivel.")
   criterio_precision_sistema: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es precision del sistema %RSD máximo de inyecciones repetidas del estándar.")
   criterio_precision_metodo: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es precision del metodo, %RSD máximo de preparaciones repetidas de muestra.")
   criterio_precision_intermedia: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es precision intermedia, %RSD máximo entre días, analistas y equipos.")
   criterio_rango: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es rango de validación niveles mínimo y máximo aceptados del método.")
   criterio_estabilidad_soluciones: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es estabilidad de las soluciones, Variación permitida vs T0 para soluciones estándar/muestra.")
   criterio_estabilidad_fase_movil: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es estabilidad de la fase movil, Condiciones aceptables de composición y desempeño cromatográfico.")
   criterio_robustez: str = Field(..., description="valor o rango, definido de antemano y respaldado científicamente, que sirve para juzgar si un parámetro de rendimiento cumple el propósito previsto del método, cuyo criterio es robustez, Cambios permitidos sin afectar resultados críticos.")

 
class Set1ExtractionModel(BaseModel):
    validacion: str = Field(..., description="Nombre del informe de validacion relacionado con la prueba del metodo analitico")
    codigo_informe: str = Field(..., description="codigo del informe de validacion")
    nombre_producto: str = Field(..., description="nombre del producto farmaceutico validado")
    codigo_producto: str = Field(..., description="codigo del producto farmaceutico")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos")
    código_protocolo_validacion: str = Field(..., description= "codigo del protocolo de validacion")
    nombre_del_protocolo_validacion: str = Field(..., description= "nombre del protocolo de validacion")
    concentracion_activos: str = Field(..., description= "concentracion de los diferentes activos")
    rango_validado: str = Field(..., description= "rango en el cual se valida el metodo")
    ctiterio_aceptacion: List[criterios] = Field(..., description= "criterio de aceptacion para cada uno de los parametros validados, los cuales se deben cumplir para que el metodo analitico se considere validado")
    parámetros_validacion: List[parametros] = Field(..., description= "son los diferentes parametros que se evaluan en un metodo analitico, como selectividad, linealidad, exactitud, precision del sistema, precision del metodo, precision intermedia, estabilidad de las soluciones, estabilidad de la fase movil, robustez")
 
class Set1RenderingModel(BaseModel):
    validacion: str = Field(..., description="Nombre del informe de validacion")
    codigo_informe: str = Field(..., description="codigo del informe de validacion")
    nombre_producto: str = Field(..., description="nombre del producto farmaceutico validado")
    codigo_producto: str = Field(..., description="codigo del producto farmaceutico")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos")
    código_protocolo_validacion: str = Field(..., description= "codigo del protocolo de validacion")
    nombre_del_protocolo_validacion: str = Field(..., description= "nombre del protocolo de validacion")
    concentracion_activos: str = Field(..., description= "concentracion de los diferentes activos")
    rango_validado: str = Field(..., description= "rango en el cual se valida el metodo")
    ctiterio_aceptacion: List[criterios] = Field(..., description= "criterio de aceptacion para cada uno de los parametros validados, los cuales se deben cumplir para que el metodo analitico se considere validado")
    parámetros_validacion: List[parametros] = Field(..., description= "son los diferentes parametros que se evaluan en un metodo analitico, como selectividad, linealidad, exactitud, precision del sistema, precision del metodo, precision intermedia, estabilidad de las soluciones, estabilidad de la fase movil, robustez")
 
class Set1StructuredOutputSupervisor(BaseModel):
    validacion: str = Field(..., description="Nombre del informe de validacion")
    codigo_informe: str = Field(..., description="codigo del informe de validacion")
    nombre_producto: str = Field(..., description="nombre del producto farmaceutico validado")
    codigo_producto: str = Field(..., description="codigo del producto farmaceutico")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos")
    código_protocolo_validacion: str = Field(..., description= "codigo del protocolo de validacion")
    nombre_del_protocolo_validacion: str = Field(..., description= "nombre del protocolo de validacion")
    concentracion_activos: str = Field(..., description= "concentracion de los diferentes activos")
    rango_validado: str = Field(..., description= "rango en el cual se valida el metodo")
    ctiterio_aceptacion: List[criterios] = Field(..., description= "criterio de aceptacion para cada uno de los parametros validados, los cuales se deben cumplir para que el metodo analitico se considere validado")
    parámetros_validacion: List[parametros] = Field(..., description= "son los diferentes parametros que se evaluan en un metodo analitico, como selectividad, linealidad, exactitud, precision del sistema, precision del metodo, precision intermedia, estabilidad de las soluciones, estabilidad de la fase movil, robustez")
 