from __future__ import annotations
"""
Local Research Query Tool – Consulta robusta de vectorstores locales
------------------------------------------------------------------
Herramienta LangChain que permite realizar consultas semánticas sobre
vectorstores persistentes (.parquet) generados por el RAG Pipeline Tool.

Características:
- Búsqueda robusta con degradación automática (MMR → similarity)
- Ajuste automático de parámetros k y fetch_k según disponibilidad
- Manejo de errores de n_neighbors <= n_samples_fit
- Formateo estructurado de resultados
- Soporte para vectorstores vacíos o corruptos

Requisitos:
- langchain, langchain_community, langchain_openai
- scikit-learn
- OPENAI_API_KEY en el entorno

Devuelve contenido formateado de documentos relevantes encontrados.
"""

import logging
from pathlib import Path
from typing import Any, Optional, Type

from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun
from langchain_core.tools import BaseTool, ToolException
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel, Field

# Configuración de logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LocalResearchQueryInput(BaseModel):
    """Schema de entrada para la Local Research Query Tool."""
    query: str = Field(
        ..., 
        description="Consulta de búsqueda semántica para realizar sobre el vectorstore"
    )
    persist_path: str = Field(
        ..., 
        description="Ruta al archivo vectorstore persistente (.parquet) a consultar"
    )
    max_results: int = Field(
        15, 
        description="Número máximo de documentos relevantes a retornar",
        ge=1,
        le=50
    )
    search_type: str = Field(
        "mmr", 
        description="Tipo de búsqueda inicial a intentar: 'mmr' o 'similarity'"
    )


class LocalResearchQueryTool(BaseTool):
    """LangChain Tool para consulta robusta de vectorstores locales con degradación automática."""
    
    name: str = "local_research_query_tool"
    description: str = """Realiza consultas semánticas robustas sobre vectorstores persistentes (.parquet). 
    Ajusta automáticamente parámetros de búsqueda para evitar errores de n_neighbors y proporciona 
    degradación automática de MMR a similarity search. Devuelve documentos relevantes formateados."""
    args_schema: Type[BaseModel] = LocalResearchQueryInput
    return_direct: bool = False
    handle_tool_error: bool = True

    @staticmethod
    def _safe_k(store: SKLearnVectorStore, desired_k: int) -> int:
        """Calcula el k seguro basado en el número de muestras disponibles en el vectorstore."""
        try:
            n_samples = len(store._embeddings)  # atributo privado pero estable
        except Exception:
            # Fallback por si la implementación interna cambia:
            n_samples = getattr(store, "_neighbors", None)
            if isinstance(n_samples, int):
                pass
            else:
                n_samples = 0
        return max(0, min(desired_k, n_samples))

    def _load_vectorstore(self, persist_path: str) -> SKLearnVectorStore:
        """Carga el vectorstore desde la ruta especificada con validación."""
        if not persist_path:
            raise ToolException("No se proporcionó ruta al vectorstore")
        
        path = Path(persist_path)
        if not path.exists():
            raise ToolException(f"El vectorstore no existe en la ruta: {persist_path}")
        
        if not path.suffix.lower() == '.parquet':
            raise ToolException(f"El archivo debe ser un vectorstore .parquet: {persist_path}")
        
        try:
            store = SKLearnVectorStore(
                embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
                persist_path=persist_path,
                serializer="parquet",
            )
            return store
        except Exception as e:
            raise ToolException(f"Error cargando vectorstore: {e}")

    def _perform_search(self, store: SKLearnVectorStore, query: str, max_results: int, search_type: str) -> str:
        """Realiza la búsqueda con degradación automática de parámetros."""
        # Calculamos cuántos vectores hay disponibles
        n_samples = self._safe_k(store, 10)  # el valor no importa aquí
        if n_samples == 0:
            return "El vectorstore está vacío – no hay documentos para buscar."

        # Secuencia de degradación basada en el tipo de búsqueda inicial
        if search_type == "mmr":
            search_plans = [
                ("mmr", min(max_results, n_samples)),
                ("mmr", min(max_results // 2, n_samples)),
                ("similarity", min(4, n_samples)),
                ("similarity", 1),
            ]
        else:
            search_plans = [
                ("similarity", min(max_results, n_samples)),
                ("similarity", min(4, n_samples)),
                ("similarity", 1),
            ]

        relevant_docs = None
        for search_method, desired_k in search_plans:
            k = self._safe_k(store, desired_k)
            if k == 0:
                continue  # nada que buscar
            
            try:
                retriever = store.as_retriever(
                    search_type=search_method,
                    search_kwargs={
                        "k": k,
                        # en MMR conviene que fetch_k ≥ k
                        "fetch_k": max(k * 2, k) if search_method == "mmr" else k,
                    },
                )
                relevant_docs = retriever.invoke(query)
                logger.info(f"Búsqueda exitosa: {search_method} (k={k}) → {len(relevant_docs)} documentos")
                break  # éxito
            except ValueError as e:
                logger.warning(f"Búsqueda {search_method} (k={k}) falló: {e}")
                continue
            except Exception as e:
                logger.error(f"Error inesperado en búsqueda {search_method} (k={k}): {e}")
                continue
        
        if relevant_docs is None:
            return "La búsqueda falló – no se pudo configurar ningún retriever."

        # Formateo del resultado
        if not relevant_docs:
            return "No se encontraron documentos relevantes para la consulta."

        formatted_docs = []
        for i, doc in enumerate(relevant_docs, 1):
            content = doc.page_content.strip()
            if content:
                formatted_docs.append(f"==DOCUMENTO {i}==\n{content}")
        
        if not formatted_docs:
            return "Los documentos encontrados no contienen contenido válido."
        
        return "\n\n".join(formatted_docs)

    def _run(
        self,
        query: str,
        persist_path: str,
        max_results: int = 15,
        search_type: str = "mmr",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Ejecuta la consulta sobre el vectorstore local."""
        
        if not query.strip():
            raise ToolException("La consulta no puede estar vacía")
        
        # Cargar vectorstore
        store = self._load_vectorstore(persist_path)
        
        # Realizar búsqueda
        result = self._perform_search(store, query, max_results, search_type)
        
        return result

    async def _arun(
        self,
        query: str,
        persist_path: str,
        max_results: int = 15,
        search_type: str = "mmr",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Versión asíncrona de la consulta al vectorstore local."""
        import asyncio
        return await asyncio.to_thread(
            self._run,
            query,
            persist_path,
            max_results,
            search_type,
            run_manager.get_sync() if run_manager else None,
        )
