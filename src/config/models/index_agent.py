from typing import Dict, List

from pydantic import BaseModel, Field

class IndexAgentResponse(BaseModel):
    """Structured response schema for INDEX-AGENT outputs."""

    vectorstore_dir_list: List[str] = Field(
        ...,
        description="Lista de rutas de vectorstores (.parquet) generadas durante la indexacion."
    )
    directories_map: Dict[str, str] = Field(
        ...,
        description="Mapa entre rutas originales solicitadas y sus vectorstores generados (o null si falla)."
    )
    summary: Dict[str, int] = Field(
        ...,
        description="Totales reportados por el pipeline de indexacion (ej. total_directories, success, failed)."
    )
    issues: List[str] = Field(
        ...,
        description="Avisos o condiciones destacadas detectadas por el agente."
    )
    errors: List[str] = Field(
        ...,
        description="Mensajes de error provenientes de las herramientas utilizadas."
    )



