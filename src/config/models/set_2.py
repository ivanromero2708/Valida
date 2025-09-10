from pydantic import BaseModel, Field
from typing import List, Optional

# Modelo de datos de variables auxiliares

class Muestra(BaseModel):
    nombre: str = Field(..., description="nombre de la muestra")
    codigo: str = Field(..., description="codigo de la muestra")
    lote: str = Field(..., description="lote de la muestra")
    codigo_interno_cim: str = Field(..., description="codigo interno de la muestra")

class Estandar(BaseModel):
    nombre: str = Field(..., description="nombre del estandar")
    fabricante: str = Field(..., description="fabricante del estandar")
    lote: str = Field(..., description="lote del estandar")
    numero_parte: str = Field(..., description="numero de parte del estandar")
    codigo_identificacion: str = Field(..., description="codigo de identificacion del estandar")
    concentracion: str = Field(..., description="concentracion del estandar")
    vencimiento: str = Field(..., description="vencimiento del estandar")

class Reactivo(BaseModel):
    nombre: str = Field(..., description="nombre del reactivo")
    fabricante: str = Field(..., description="fabricante del reactivo")
    lote: str = Field(..., description="lote del reactivo")
    numero_parte: str = Field(..., description="numero de parte del reactivo")
    vencimiento: str = Field(..., description="vencimiento del reactivo")

class Material(BaseModel):
    nombre: str = Field(..., description="nombre del material")
    fabricante: str = Field(..., description="fabricante del material")
    numero_parte: str = Field(..., description="numero de parte del material")
    lote: str = Field(..., description="lote del material")

class Equipo(BaseModel):
    nombre: str = Field(..., description="nombre del equipo")
    consecutivo: str = Field(..., description="consecutivo del equipo")
    fabricante: str = Field(..., description="fabricante del equipo")
    modelo: str = Field(..., description="modelo del equipo")
    serial: Optional[str] = Field(None, description="serial del equipo")
    prox_actividad: str = Field(..., description="proxima actividad del equipo")

class Columna(BaseModel):
    descripcion: str = Field(..., description="descripcion de la columna")
    fabricante: str = Field(..., description="fabricante de la columna")
    numero_parte: str = Field(..., description="numero de parte de la columna")
    serial: Optional[str] = Field(None, description="serial de la columna")
    numero_interno: str = Field(..., description="numero interno de la columna")

# Modelos de validación de datos

class Set2ExtractionModel(BaseModel):
    muestra_utilizadas: List[Muestra] = Field(..., description = "Listado de muestras utilizadas")
    estandar_utilizados: List[Estandar] = Field(..., description = "Listado de estandares utilizados")
    reactivo_utilizados: List[Reactivo] = Field(..., description = "Listado de reactivos utilizados")
    materiales_utilizados: List[Material] = Field(..., description = "Listado de materiales utilizados")
    equipos_utilizados: List[Equipo] = Field(..., description = "Listado de equipos utilizados")
    columna_utilizada: List[Columna] = Field(..., description = "Listado de columnas utilizadas")  

class Set2RenderingModel(BaseModel):
    muestra_utilizadas: List[Muestra] = Field(..., description = "Listado de muestras utilizadas")
    estandar_utilizados: List[Estandar] = Field(..., description = "Listado de estandares utilizados")
    reactivo_utilizados: List[Reactivo] = Field(..., description = "Listado de reactivos utilizados")
    materiales_utilizados: List[Material] = Field(..., description = "Listado de materiales utilizados")
    equipos_utilizados: List[Equipo] = Field(..., description = "Listado de equipos utilizados")
    columna_utilizada: List[Columna] = Field(..., description = "Listado de columnas utilizadas")  

class Set2StructuredOutputSupervisor(BaseModel):
    muestra_utilizadas: List[Muestra] = Field(..., description = "Listado de muestras utilizadas")
    estandar_utilizados: List[Estandar] = Field(..., description = "Listado de estandares utilizados")
    reactivo_utilizados: List[Reactivo] = Field(..., description = "Listado de reactivos utilizados")
    materiales_utilizados: List[Material] = Field(..., description = "Listado de materiales utilizados")
    equipos_utilizados: List[Equipo] = Field(..., description = "Listado de equipos utilizados")
    columna_utilizada: List[Columna] = Field(..., description = "Listado de columnas utilizadas")  
