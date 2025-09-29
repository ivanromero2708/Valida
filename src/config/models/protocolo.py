from pydantic import BaseModel, Field
from typing import Literal, List

class ParametroValidacion(BaseModel):
    parametro: Literal["Selectividad","Linealidad","Exactitud","Precision Sistema","Precision Metodo","Precision Intermedia","Rango","Estabilidad Soluciones","Estabilidad Fase Movil","Robustez"] = Field(..., description = "Parametro de validacion")
    descripcion: str = Field(..., description = "Descripcion del parametro de validacion")

class ParametrosValidacion(BaseModel):
    parametros: List[ParametroValidacion] = Field(..., description = "Parametros de validacion")