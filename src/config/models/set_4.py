from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Set 4 - Plan de razonamiento
# - Múltiples arrays de objetos para materiales, cada uno con campos específicos
# - muestra_utilizadas[]: Lista de objetos Muestra con nombre, codigo, lote, codigo_interno_cim
# - estandar_utilizados[]: Lista de objetos Estandar con nombre, fabricante, lote, numero_parte, codigo_identificacion, concentracion, vencimiento
# - reactivo_utilizados[]: Lista de objetos Reactivo con nombre, fabricante, lote, numero_parte, vencimiento
# - materiales_utilizados[]: Lista de objetos Material con nombre, fabricante, numero_parte, lote
# - equipos_utilizados[]: Lista de objetos Equipo con nombre, consecutivo, fabricante, modelo, serial, prox_actividad

class MuestraUtilizada(BaseModel):
    nombre: str
    codigo: str
    lote: Optional[str] = None
    codigo_interno_cim: str

class EstandarUtilizado(BaseModel):
    nombre: str
    fabricante: str
    lote: str
    numero_parte: str
    codigo_identificacion: str
    concentracion: str
    vencimiento: date

class ReactivoUtilizado(BaseModel):
    nombre: str
    fabricante: str
    lote: str
    numero_parte: str
    vencimiento: date

class MaterialUtilizado(BaseModel):
    nombre: str
    fabricante: str
    numero_parte: str
    lote: str

class EquipoUtilizado(BaseModel):
    nombre: str
    consecutivo: str
    fabricante: str
    modelo: str
    serial: str
    prox_actividad: date

class Set4ExtractionModel(BaseModel):
    muestra_utilizadas: List[MuestraUtilizada]
    estandar_utilizados: List[EstandarUtilizado]
    reactivo_utilizados: List[ReactivoUtilizado]
    materiales_utilizados: List[MaterialUtilizado]
    equipos_utilizados: List[EquipoUtilizado]

class Set4RenderingModel(BaseModel):
    muestra_utilizadas: List[MuestraUtilizada]
    estandar_utilizados: List[EstandarUtilizado]
    reactivo_utilizados: List[ReactivoUtilizado]
    materiales_utilizados: List[MaterialUtilizado]
    equipos_utilizados: List[EquipoUtilizado]

class Set4StructuredOutputSupervisor(BaseModel):
    muestra_utilizadas: List[MuestraUtilizada]
    estandar_utilizados: List[EstandarUtilizado]
    reactivo_utilizados: List[ReactivoUtilizado]
    materiales_utilizados: List[MaterialUtilizado]
    equipos_utilizados: List[EquipoUtilizado]