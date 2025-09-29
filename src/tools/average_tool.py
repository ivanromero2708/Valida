from __future__ import annotations

import json
import statistics
from datetime import datetime
from typing import List, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class AverageInput(BaseModel):
    """Esquema de entrada para `AverageTool`."""

    valores: List[float] = Field(
        ..., description="Lista de valores numéricos para calcular el promedio", min_items=1
    )


class AverageTool(BaseTool):
    """Herramienta que calcula el promedio aritmético de una lista de valores."""

    name: str = "average_tool"
    description: str = (
        "Calcula el promedio aritmético de una lista de valores numéricos. "
        "Entrada: `valores` (lista de floats). Retorna JSON con el promedio y el conteo."
    )
    args_schema: Type[BaseModel] = AverageInput
    return_direct: bool = False
    handle_tool_error: bool = True

    def _run(
        self,
        valores: List[float],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            datos = AverageInput(valores=valores)
            promedio = float(statistics.fmean(datos.valores))
            respuesta = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "count": len(datos.valores),
                "mean": promedio,
            }
            return json.dumps(respuesta, ensure_ascii=False)
        except Exception as exc:  # pragma: no cover - manejo genérico para LangChain
            error_response = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error_message": str(exc),
                "error_type": type(exc).__name__,
            }
            return json.dumps(error_response, ensure_ascii=False)

    async def _arun(
        self,
        valores: List[float],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        import asyncio

        sync_manager = run_manager.get_sync() if run_manager else None
        return await asyncio.to_thread(self._run, valores, sync_manager)
