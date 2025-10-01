from __future__ import annotations
"""
Linealidad Tool – Análisis de regresión lineal para curvas de calibración
------------------------------------------------------------------------
Herramienta diseñada para el flujo de agentes que recibe datos de concentración
y área de picos directamente, sin fallbacks de lectura de archivos.

Características:
- Cálculo de regresión lineal (pendiente, intercepto, R²)
- Análisis de residuales
- Cálculo de %RSD por nivel de concentración
- Generación de gráficos (regresión y residuales)
- Salida en formato JSON estructurado
- Compatible con LangGraph y flujo de agentes

Requisitos:
- numpy, matplotlib, pydantic
- langchain_core
"""

import json
import logging
import os
import io
import base64
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from src.utils.pathing import get_images_root

import numpy as np
# Configurar matplotlib para usar backend sin GUI antes de importar pyplot
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI, seguro para hilos secundarios
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field, validator
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
    AsyncCallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configuración de matplotlib
try:
    plt.rcParams["font.family"] = "Times New Roman"
except Exception:
    plt.rcParams["font.family"] = "serif"

plt.rcParams["font.size"] = 12
TITLE_SIZE = 14
LABEL_SIZE = 12
TICK_SIZE = 11
LEGEND_SIZE = 11


class LinearidadInput(BaseModel):
    """Esquema de entrada para la herramienta de linealidad."""
    
    concentracion: List[float] = Field(
        ..., 
        description="Lista de concentraciones (X) en mg/mL",
        min_items=2
    )
    area_pico: List[float] = Field(
        ..., 
        description="Lista de áreas de pico (Y) correspondientes",
        min_items=2
    )
    devolver_base64: bool = Field(
        default=False, 
        description="Si True, incluye gráficos en base64 en la respuesta"
    )
    nombre_analito: Optional[str] = Field(
        default=None,
        description="Nombre del analito para títulos de gráficos"
    )

class LinearidadCalculator:
    """Clase para realizar cálculos de linealidad."""
    
    @staticmethod
    def calcular_regresion_lineal(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Calcula regresión lineal y estadísticas asociadas.
        
        Args:
            x: Array de concentraciones
            y: Array de áreas de pico
            
        Returns:
            Dict con resultados de regresión
        """
        # Regresión lineal
        m, b = np.polyfit(x, y, 1)
        y_hat = m * x + b
        
        # Coeficiente de determinación (R²)
        ss_res = float(np.sum((y - y_hat) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
        
        # Residuales
        residuales = y - y_hat
        
        # %RSD por nivel de concentración (para replicados)
        rsd_por_nivel = {}
        unique_x = sorted(set(x.tolist()))
        
        for xv in unique_x:
            mask = x == xv
            y_sub = y[mask]
            if y_sub.size >= 2:
                mean_val = float(np.mean(y_sub))
                std_val = float(np.std(y_sub, ddof=1))
                rsd = float(std_val / mean_val * 100.0) if mean_val != 0 else float("nan")
                rsd_por_nivel[f"{xv:g}"] = rsd
        
        # Estadísticas de residuales
        residuales_stats = {
            "media": float(np.mean(residuales)),
            "desv_est": float(np.std(residuales, ddof=1)) if len(residuales) > 1 else 0.0,
            "max_absoluto": float(np.max(np.abs(residuales))),
            "min": float(np.min(residuales)),
            "max": float(np.max(residuales))
        }
        
        return {
            "pendiente_m": float(m),
            "intercepto_b": float(b),
            "r2": float(r2),
            "y_predicho": y_hat.tolist(),
            "residuales": residuales.tolist(),
            "rsd_por_nivel_pct": rsd_por_nivel,
            "residuales_stats": residuales_stats,
            "ecuacion": f"y = {m:.6f}x + {b:.6f}"
        }


class LinearidadPlotter:
    """Clase para generar gráficos de linealidad."""
    

    @staticmethod
    def plot_regresion(
        x: np.ndarray,
        y: np.ndarray,
        y_hat: np.ndarray,
        m: float,
        b: float,
        r2: float,
        nombre_analito: Optional[str] = None
    ):
        """Genera gráfico de regresión lineal."""
        idx = np.argsort(x)
        x_ord, y_hat_ord = x[idx], y_hat[idx]

        fig, ax = plt.subplots(figsize=(10, 7), dpi=120)
        ax.scatter(x, y, color="black", s=60, alpha=0.8, label="Datos experimentales")
        ax.plot(
            x_ord,
            y_hat_ord,
            color="blue",
            linewidth=2.5,
            label=f"y = {m:.6f}x + {b:.6f}"
        )

        ax.set_xlabel("Concentración (mg/mL)", fontsize=LABEL_SIZE, fontweight='bold')
        ax.set_ylabel("Área del pico", fontsize=LABEL_SIZE, fontweight='bold')

        titulo = "Curva de Calibración - Análisis de Linealidad"
        if nombre_analito:
            titulo += f"\n{nombre_analito}"
        ax.set_title(titulo, fontsize=TITLE_SIZE, fontweight='bold', pad=20)

        ax.text(
            0.05,
            0.95,
            f"R² = {r2:.6f}",
            transform=ax.transAxes,
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8)
        )

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=LEGEND_SIZE, loc='lower right')
        ax.tick_params(axis="both", labelsize=TICK_SIZE)
        fig.tight_layout()

        return fig

    @staticmethod
    def plot_residuales(
        x: np.ndarray,
        residuales: np.ndarray,
        nombre_analito: Optional[str] = None
    ):
        """Genera gráfico de residuales."""
        fig, ax = plt.subplots(figsize=(10, 7), dpi=120)
        ax.scatter(x, residuales, color="red", s=60, alpha=0.8, label="Residuales")
        ax.axhline(0, color="blue", linestyle="--", linewidth=2, alpha=0.7, label="y = 0")

        ax.set_xlabel("Concentración (mg/mL)", fontsize=LABEL_SIZE, fontweight='bold')
        ax.set_ylabel("Residual", fontsize=LABEL_SIZE, fontweight='bold')

        titulo = "Análisis de Residuales"
        if nombre_analito:
            titulo += f"\n{nombre_analito}"
        ax.set_title(titulo, fontsize=TITLE_SIZE, fontweight='bold', pad=20)

        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=LEGEND_SIZE)
        ax.tick_params(axis="both", labelsize=TICK_SIZE)
        fig.tight_layout()

        return fig

    @staticmethod
    def save_plot(fig, path: str) -> str:
        """Guarda gráfico en disco y retorna la ruta absoluta."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor='white')
        plt.close(fig)
        return os.path.abspath(path)

    @staticmethod
    def fig_to_base64(fig) -> str:
        """Convierte figura a string base64."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor='white')
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)
        return b64


class LinearidadTool(BaseTool):
    """
    Herramienta de análisis de linealidad para curvas de calibración.
    
    Recibe datos de concentración y área de picos directamente del flujo de agentes,
    realiza análisis de regresión lineal y genera reportes estructurados.
    """
    
    name: str = "linealidad_tool"
    description: str = (
        "Analiza la linealidad de curvas de calibración mediante regresión lineal. "
        "Calcula pendiente, intercepto, R², residuales y %RSD por nivel. "
        "Genera gráficos de regresión y residuales. Entrada: listas de concentración y área."
    )
    args_schema: Type[BaseModel] = LinearidadInput
    return_direct: bool = False
    handle_tool_error: bool = True

    def _run(
        self,
        concentracion: List[float],
        area_pico: List[float],
        devolver_base64: bool = False,
        nombre_analito: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Ejecuta el análisis de linealidad.
        
        Returns:
            JSON string con resultados del análisis
        """
        try:
            # Validar entrada
            input_data = LinearidadInput(
                concentracion=concentracion,
                area_pico=area_pico,
                devolver_base64=devolver_base64,
                nombre_analito=nombre_analito
            )
            
            logger.info(f"[LinearidadTool] Iniciando análisis con {len(concentracion)} puntos")
            
            # Convertir a arrays numpy
            x = np.array(concentracion, dtype=float)
            y = np.array(area_pico, dtype=float)
            
            # Realizar cálculos de regresión
            calculator = LinearidadCalculator()
            resultados = calculator.calcular_regresion_lineal(x, y)
            
            # Generar gráficos si se solicita
            plots_info = {
                "regresion_png_path": None,
                "residuales_png_path": None,
                "regresion_base64": None,
                "residuales_base64": None
            }
            
            # Siempre generar y guardar gráficos (requerido para flujo de agentes)
            plotter = LinearidadPlotter()
            
            # Crear directorio de imágenes de salida configurable
            images_dir = get_images_root()
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar UUIDs únicos para los archivos
            uuid_regresion = str(uuid.uuid4())
            uuid_residuales = str(uuid.uuid4())
            
            try:
                # Gráfico de regresión
                fig_reg = plotter.plot_regresion(
                    x, y, np.array(resultados["y_predicho"]),
                    resultados["pendiente_m"], resultados["intercepto_b"], 
                    resultados["r2"], nombre_analito
                )
                
                # Siempre guardar gráfico de regresión
                reg_path = images_dir / f"linealidad_regresion_{uuid_regresion}.png"
                plots_info["regresion_png_path"] = plotter.save_plot(fig_reg, str(reg_path))
                logger.info(f"[LinearidadTool] Gráfico de regresión guardado: {reg_path}")
                
                # Gráfico de residuales
                fig_res = plotter.plot_residuales(
                    x, np.array(resultados["residuales"]), nombre_analito
                )
                
                # Siempre guardar gráfico de residuales
                res_path = images_dir / f"linealidad_residuales_{uuid_residuales}.png"
                plots_info["residuales_png_path"] = plotter.save_plot(fig_res, str(res_path))
                logger.info(f"[LinearidadTool] Gráfico de residuales guardado: {res_path}")
                
                # Generar base64 solo si se solicita
                if devolver_base64:
                    # Re-generar para base64 limpio
                    fig_reg_b64 = plotter.plot_regresion(
                        x, y, np.array(resultados["y_predicho"]),
                        resultados["pendiente_m"], resultados["intercepto_b"], 
                        resultados["r2"], nombre_analito
                    )
                    plots_info["regresion_base64"] = plotter.fig_to_base64(fig_reg_b64)
                    
                    fig_res_b64 = plotter.plot_residuales(
                        x, np.array(resultados["residuales"]), nombre_analito
                    )
                    plots_info["residuales_base64"] = plotter.fig_to_base64(fig_res_b64)
                    
            except Exception as e:
                logger.warning(f"[LinearidadTool] Error generando gráficos: {e}")
            
            # Ensamblar respuesta final
            respuesta = {
                "regresion_png_path": plots_info["regresion_png_path"],
                "residuales_png_path": plots_info["residuales_png_path"],
            }
            
            logger.info(f"[LinearidadTool] Análisis completado exitosamente. R² = {resultados['r2']:.6f}")
            
            return json.dumps(respuesta, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"[LinearidadTool] Error en análisis: {e}")
            error_response = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error_message": str(e),
                "error_type": type(e).__name__
            }
            return json.dumps(error_response, indent=2, ensure_ascii=False)

    async def _arun(
        self,
        concentracion: List[float],
        area_pico: List[float],
        devolver_base64: bool = False,
        nombre_analito: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Versión asíncrona del análisis de linealidad."""
        import asyncio
        
        return await asyncio.to_thread(
            self._run,
            concentracion,
            area_pico,
            devolver_base64,
            nombre_analito,
            run_manager.get_sync() if run_manager else None,
        )

