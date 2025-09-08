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

class ActivoBasico(BaseModel):
    nombre: str

class Set1ExtractionModel(BaseModel):
    pass

class Set1RenderingModel(BaseModel):
    validacion: str
    codigo_informe: str
    nombre_producto: str
    codigo_producto: str
    lista_activos: List[str]
    concentracion_activos: str
    rango_validado: str
    activos: List[ActivoBasico]

class Set1StructuredOutputSupervisor(BaseModel):
    validacion: str
    codigo_informe: str
    nombre_producto: str
    codigo_producto: str
    lista_activos: List[str]
    concentracion_activos: str
    rango_validado: str
    activos: List[ActivoBasico]