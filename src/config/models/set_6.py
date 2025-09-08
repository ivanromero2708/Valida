from pydantic import BaseModel
from typing import List

# Set 6 - Plan de razonamiento
# - columna_utilizada[]: Lista de objetos ColumnaUtilizada
# - Cada columna tiene descripcion, fabricante, numero_parte, serial, numero_interno

class ColumnaUtilizada(BaseModel):
    descripcion: str
    fabricante: str
    numero_parte: str
    serial: str
    numero_interno: str

class Set6ExtractionModel(BaseModel):
    columna_utilizada: List[ColumnaUtilizada]

class Set6RenderingModel(BaseModel):
    columna_utilizada: List[ColumnaUtilizada]

class Set6StructuredOutputSupervisor(BaseModel):
    columna_utilizada: List[ColumnaUtilizada]