from __future__ import annotations

import json
import math
from datetime import datetime
from typing import List, Optional, Type

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class RSDInput(BaseModel):
    """Esquema de entrada para `RSDTool`."""

    valores: List[float] = Field(
        ..., description="Lista de valores numéricos para calcular el %RSD", min_items=2
    )


class RSDTool(BaseTool):
    """Herramienta que calcula el porcentaje de desviación estándar relativa (%RSD)."""

    name: str = "rsd_tool"
    description: str = (
        "Calcula el porcentaje de desviación estándar relativa para una lista de valores. "
        "Entrada: `valores` (lista de floats). Retorna JSON con la media, desviación estándar y %RSD."
    )
    args_schema: Type[BaseModel] = RSDInput
    return_direct: bool = False
    handle_tool_error: bool = True

    def _run(
        self,
        valores: List[float],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        try:
            datos = RSDInput(valores=valores)
            media = sum(datos.valores) / len(datos.valores)
            if math.isclose(media, 0.0, abs_tol=1e-12):
                raise ValueError("La media es cero, no se puede calcular el %RSD.")

            # Desviación estándar muestral (ddof=1)
            mean_diff_sq = [pow(v - media, 2) for v in datos.valores]
            variance = sum(mean_diff_sq) / (len(datos.valores) - 1)
            std_dev = math.sqrt(variance)
            rsd = (std_dev / abs(media)) * 100.0

            respuesta = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "count": len(datos.valores),
                "mean": media,
                "std_dev": std_dev,
                "rsd_pct": rsd,
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
