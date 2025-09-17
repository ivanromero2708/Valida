from __future__ import annotations
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SKLearnVectorStore
from langchain_core.tools import tool
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _safe_k(store: SKLearnVectorStore, desired_k: int) -> int:
    """Devuelve min(desired_k, n_samples)."""
    try:
        # Primary method: try to load the parquet file directly to count rows
        # This is the most reliable method since SKLearnVectorStore may not load data into memory immediately
        import pandas as pd
        import os
        if hasattr(store, 'persist_path') and store.persist_path and os.path.exists(store.persist_path):
            df = pd.read_parquet(store.persist_path)
            n_samples = len(df)
            logger.debug(f"_safe_k: found {n_samples} samples from parquet file")
        else:
            # Fallback methods if parquet file is not accessible
            if hasattr(store, '_embeddings') and store._embeddings is not None:
                n_samples = len(store._embeddings)
                logger.debug(f"_safe_k: found {n_samples} samples from _embeddings")
            elif hasattr(store, 'docstore') and hasattr(store.docstore, '_dict'):
                n_samples = len(store.docstore._dict)
                logger.debug(f"_safe_k: found {n_samples} samples from docstore")
            else:
                n_samples = 0
                logger.debug("_safe_k: no data found, returning 0")
    except Exception as e:
        logger.debug(f"Failed to determine n_samples: {e}")
        n_samples = 0
    
    result = max(0, min(desired_k, n_samples))
    logger.debug(f"_safe_k: returning {result} (desired_k={desired_k}, n_samples={n_samples})")
    return result


@tool
def local_research_query_tool(query: str, persist_path: str) -> str:
    """
    Consulta de documentos locales usando un retriever robusto.

    Ajusta automáticamente k y fetch_k para evitar:
        ValueError: Expected n_neighbors <= n_samples_fit …
    """
    if not persist_path:
        return "There is no provided documentation to search in."

    # 1. Cargamos el vectorstore
    store = SKLearnVectorStore(
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_path=persist_path,
        serializer="parquet",
    )

    # 2. Calculamos cuántos vectores hay
    n_samples = _safe_k(store, 10)  # no importa el desired_k aquí
    if n_samples == 0:
        return "Vectorstore is empty – no documents to search."

    # 3. Manejo especial para vectorstores con un solo documento
    if n_samples == 1:
        try:
            retriever = store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 1}
            )
            relevant_docs = retriever.invoke(query)
            logger.debug("Single document retrieval → %s docs", len(relevant_docs))
        except Exception as e:
            logger.warning("Single document retrieval failed: %s", e)
            relevant_docs = None
    else:
        # 4. Secuencia de degradación para múltiples documentos: MMR(15) → MMR(n_samples) → similarity(4→1)
        search_plans = [
            ("mmr", 15),
            ("mmr", n_samples),
            ("similarity", min(4, n_samples)),
            ("similarity", 1),
        ]

        relevant_docs = None
        for search_type, desired_k in search_plans:
            k = _safe_k(store, desired_k)
            if k == 0:
                continue  # nada que buscar
            try:
                # Calculamos fetch_k seguro para MMR
                if search_type == "mmr":
                    fetch_k = _safe_k(store, max(k * 2, k))
                else:
                    fetch_k = k
                    
                retriever = store.as_retriever(
                    search_type=search_type,
                    search_kwargs={
                        "k": k,
                        "fetch_k": fetch_k,
                    },
                )
                relevant_docs = retriever.invoke(query)
                logger.debug("Retriever %s (k=%s) → %s docs", search_type, k, len(relevant_docs))
                break  # éxito
            except ValueError as e:
                logger.warning("Searcher %s (k=%s) failed: %s", search_type, k, e)
                continue
        else:
            return "Search failed – no retriever could be configured."

    # 4. Formateo del resultado
    if not relevant_docs:
        return "No relevant documents found."

    formatted = "\n\n".join(
        f"==DOCUMENT {i+1}==\n{doc.page_content}" for i, doc in enumerate(relevant_docs)
    )
    return formatted
