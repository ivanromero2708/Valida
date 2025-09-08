from pydantic import BaseModel, Field
from typing import List

# Set 3 - Plan de razonamiento
# - código_protocolo_validacion: tipo str, obligatorio - código del protocolo (con tilde)
# - nombre_del_protocolo_validacion: tipo str, obligatorio - nombre del protocolo
# - parámetros_de_validacion[]: tipo List[str], obligatorio - lista de parámetros (con tilde)

class Set3ExtractionModel(BaseModel):
    código_protocolo_validacion: str = Field(alias="codigo_protocolo_validacion")
    nombre_del_protocolo_validacion: str
    parámetros_de_validacion: List[str] = Field(alias="parametros_de_validacion")

class Set3RenderingModel(BaseModel):
    código_protocolo_validacion: str = Field(alias="codigo_protocolo_validacion")
    nombre_del_protocolo_validacion: str
    parámetros_de_validacion: List[str] = Field(alias="parametros_de_validacion")

class Set3StructuredOutputSupervisor(BaseModel):
    código_protocolo_validacion: str = Field(alias="codigo_protocolo_validacion")
    nombre_del_protocolo_validacion: str
    parámetros_de_validacion: List[str] = Field(alias="parametros_de_validacion")