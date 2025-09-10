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
 
class API(BaseModel):
    nombre: str = Field(..., description="Nombre del ingrediente activo.")
    concentracion: str = Field(..., description="Concentración del ingrediente activo")
 
class Set1ExtractionModel(BaseModel):
    validacion: str = Field(..., description="Nombre del informe de validacion")
    codigo_informe: str = Field(..., description="codigo del informe de validacion")
    nombre_producto: str = Field(..., description="nombre del producto farmaceutico validado")
    codigo_producto: str = Field(..., description="codigo del producto farmaceutico")
    lista_activos: List[API] = Field(..., description="Lista de ingredientes activos")
    código_protocolo_validacion: str = Field(..., description= "codigo del protocolo de validacion")
    nombre_del_protocolo_validacion: str = Field(..., description= "nombre del protocolo de validacion")
    concentracion_activos: str = Field(..., description= "concentracion de los diferentes activos")
    rango_validado: str = Field(..., description= "rango en el cual se valida el metodo")
    parámetros_de_validacion: List[str] = Field(..., description= "parametros que se validaran")
 
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
    parámetros_de_validacion: List[str] = Field(..., description= "parametros que se validaran")
 
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
    parámetros_de_validacion: List[str] = Field(..., description= "parametros que se validaran")
 