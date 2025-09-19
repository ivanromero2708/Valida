# tools.py
import os
from typing import Any, Callable, Dict, List

# --- Importa tus herramientas personalizadas ---
from src.tools.rag_pipeline_tool import RAGPipelineTool
from src.tools.local_research_query_tool import local_research_query_tool
from src.tools.linealidad_tool import LinearidadTool

# --- Instanciación de las herramientas basadas en clases ---
rag_pipeline_tool = RAGPipelineTool()
linearidad_tool = LinearidadTool()

# --- Registro Central de Herramientas ---
# Usamos un diccionario para que sea fácil de mantener y escalar.
# La clave es el nombre que usará el agente, y el valor es el objeto de la herramienta.
AVAILABLE_TOOLS: Dict[str, Any] = {
    # Herramientas de Búsqueda
    "rag_pipeline_tool": rag_pipeline_tool,
    "local_research_query_tool": local_research_query_tool,
    "linearidad_tool": linearidad_tool,
}


def get_tools(selected_tools: List[str]) -> List[Any]:
    """
    Convierte una lista de nombres de herramientas en los objetos de herramienta correspondientes.
    Busca cada nombre en el diccionario AVAILABLE_TOOLS y devuelve las que encuentra.
    """
    # Esta es la forma moderna y eficiente de hacerlo, en lugar de un `if/elif`.
    return [AVAILABLE_TOOLS[name] for name in selected_tools if name in AVAILABLE_TOOLS]

