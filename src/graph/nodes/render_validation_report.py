"""Renderizador de reportes de validación para el sistema Valida."""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langsmith import traceable

from src.graph.state import ValidaState

try:
    from docxtpl import DocxTemplate
    from jinja2.exceptions import UndefinedError
except ImportError:
    DocxTemplate = None
    UndefinedError = None
    logging.warning("docxtpl not installed. DOCX rendering will not be available.")

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = _BASE_DIR / "templates" / "validation_template20250915.docx"
OUTPUT_DIR = _BASE_DIR / "output"

class RenderValidationReport:
    """Renderiza reportes de validación en plantillas DOCX para el sistema Valida."""

    def __init__(self, template_path: Optional[Path] = None) -> None:
        # Permite inyectar un path; si no, usa el default
        self.template_path = Path(template_path) if template_path else TEMPLATE_PATH

    # ---------- Utilidades internas ----------
    def _state_get(self, state: Any, key: str, default: Any = "") -> Any:
        """Obtiene valores del estado tanto si es dict como si es objeto (p. ej., Pydantic)."""
        if isinstance(state, dict):
            return state.get(key, default)
        # getattr para modelos/objetos; si no existe, devuelve default
        return getattr(state, key, default)

    def _clean_text(self, text: str) -> str:
        """Limpia texto para evitar caracteres no válidos en DOCX y normaliza Unicode."""
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        # Normaliza Unicode
        text = unicodedata.normalize("NFC", text)
        # Remueve caracteres de control no permitidos por docx
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
        # Normaliza saltos de línea
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Colapsa espacios repetidos (no toca saltos de línea)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _add_default_values(self, data: Dict[str, Any]) -> None:
        """Asegura que None -> '' y deja listas/dicts intactos."""
        to_fix = {}
        for k, v in data.items():
            if v is None:
                to_fix[k] = ""
        data.update(to_fix)

    def _merge_contexts(self, base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
        """Fusión simple: las claves de extra sobrescriben base."""
        merged = dict(base)
        merged.update(extra)
        return merged

    def _extract_undefined_key(self, err_msg: str) -> Optional[str]:
        """
        Intenta extraer la clave undefined del mensaje de Jinja2.
        Ejemplos comunes: "'foo' is undefined" o "UndefinedError: 'bar' is undefined"
        """
        m = re.search(r"'([^']+)'\s+is\s+undefined", err_msg)
        return m.group(1) if m else None

    def _render_with_fallback_missing(self, doc: DocxTemplate, context: Dict[str, Any], max_retries: int = 30) -> None:
        """
        Intenta renderizar. Si hay variables undefined, las define como '' y reintenta, hasta max_retries.
        Esto evita romper por claves faltantes en plantillas muy grandes/dinámicas.
        """
        attempt = 0
        while True:
            try:
                doc.render(context)
                return
            except UndefinedError as e:
                attempt += 1
                if attempt > max_retries:
                    raise
                missing = self._extract_undefined_key(str(e)) or ""
                if missing:
                    logger.warning(f"Variable faltante en plantilla: '{missing}'. Se rellenará con ''. (Intento {attempt})")
                    context.setdefault(missing, "")
                else:
                    # Si no se pudo extraer, abortamos para no ciclar
                    raise

    # ---------- Agregación de contexto ----------
    @traceable
    def _aggregate_context(self, context_list: List[Any]) -> Dict[str, Any]:
        """Agrega y limpia el contexto de todos los sets."""
        aggregated: Dict[str, Any] = {}
        if not context_list:
            return aggregated

        logger.info(f"Procesando {len(context_list)} items de contexto")

        for i, item in enumerate(context_list):
            try:
                # Puede venir como dict o como objeto con atributo context_for_set
                if isinstance(item, dict):
                    ctx = item.get("context_for_set", item)
                else:
                    ctx = getattr(item, "context_for_set", {}) or {}

                if isinstance(ctx, dict):
                    cleaned_ctx: Dict[str, Any] = {}
                    for key, value in ctx.items():
                        if isinstance(value, str):
                            cleaned_value = self._clean_text(value)
                            cleaned_ctx[key] = cleaned_value
                            logger.debug(f"Set {i+1} | Limpio {key}: '{value}' -> '{cleaned_value}'")
                        else:
                            cleaned_ctx[key] = value
                    aggregated.update(cleaned_ctx)
                    logger.info(f"Set {i+1}: agregadas {len(cleaned_ctx)} claves")
                else:
                    logger.warning(f"Set {i+1}: contexto no es dict: {type(ctx)}")

            except Exception as e:
                logger.error(f"Error procesando contexto {i+1}: {e}", exc_info=True)
                continue

        # Defaults simples
        self._add_default_values(aggregated)

        logger.info(f"Contexto final agregado: {len(aggregated)} claves totales")
        return aggregated

    # ---------- Nodo principal ----------
    @traceable
    def run(self, state: ValidaState, config: RunnableConfig) -> Command[Literal["__end__"]]:
        """
        Ejecuta el renderizado del reporte de validación.

        Returns:
            Command con estado actualizado y finalización del flujo.
        """
        # Verificar disponibilidad de la librería
        if DocxTemplate is None:
            logger.error("docxtpl no está instalado. No es posible renderizar el DOCX.")
            return Command(
                update={
                    "messages": [
                        HumanMessage(
                            content="No se pudo generar el reporte: falta la librería docxtpl.",
                            name="render_validation_report",
                        )
                    ]
                },
                goto="__end__",
            )

        # 0) Permite override de plantilla desde el estado
        tpl_override = self._state_get(state, "template_path", None) or self._state_get(state, "doc_template_path", None)
        tpl_path = Path(tpl_override) if tpl_override else Path(self.template_path)

        # 1) Aplanar el contexto acumulado de todos los supervisores
        context_list = self._state_get(state, "context_for_render", []) or []
        tags_map = self._aggregate_context(context_list)

        # 2) Agregar información básica del estado
        basic_context = {
            "validacion": self._state_get(state, "validacion", ""),
            "codigo_informe": self._state_get(state, "codigo_informe", ""),
            "nombre_producto": self._state_get(state, "nombre_producto", ""),
            "codigo_producto": self._state_get(state, "codigo_producto", ""),
            "rango_validado": self._state_get(state, "rango_validado", ""),
            "fecha_render": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lista_activos": [
                {
                    "nombre": getattr(api, 'nombre', ''),
                    "concentracion": getattr(api, 'concentracion', '')
                }
                for api in self._state_get(state, "lista_activos", [])
            ]
        }

        # 3) Agregar contextos específicos de validación
        validation_context = {
            "linearity_data": self._state_get(state, "linearity_data", ""),
            "accuracy_data": self._state_get(state, "accuracy_data", ""),
            "precision_data": self._state_get(state, "precision_data", ""),
            "repeatability_data": self._state_get(state, "repeatability_data", ""),
            "intermediate_precision_data": self._state_get(state, "intermediate_precision_data", ""),
            "solution_stability_data": self._state_get(state, "solution_stability_data", ""),
            "mobile_phase_stability_data": self._state_get(state, "mobile_phase_stability_data", ""),
            "robustness_data": self._state_get(state, "robustness_data", ""),
            "materials_supplies_data": self._state_get(state, "materials_supplies_data", ""),
        }

        # 4) Combinar y limpiar texto
        final_context = self._merge_contexts(self._merge_contexts(basic_context, tags_map), validation_context)
        for key, value in list(final_context.items()):
            if isinstance(value, str):
                final_context[key] = self._clean_text(value)
            elif value is None:
                final_context[key] = ""

        # 5) Validar plantilla
        if not tpl_path.exists():
            logger.error(f"Plantilla no encontrada: {tpl_path}")
            return Command(
                update={
                    "messages": [
                        HumanMessage(
                            content=f"No se encontró la plantilla en {tpl_path}",
                            name="render_validation_report",
                        )
                    ]
                },
                goto="__end__",
            )

        # 6) Renderizar y guardar
        try:
            doc = DocxTemplate(str(tpl_path))
            # Intento robusto ante variables faltantes
            if UndefinedError is not None:
                self._render_with_fallback_missing(doc, final_context, max_retries=50)
            else:
                doc.render(final_context)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname_out = OUTPUT_DIR / f"validation_report_{timestamp}.docx"
            doc.save(str(fname_out))

            msg = f"Reporte de validación generado en: {fname_out}"
            logger.info(msg)

            return Command(
                update={
                    "messages": [HumanMessage(content=msg, name="render_validation_report")],
                    "fname_out": str(fname_out),
                    "render_template": str(tpl_path),
                },
                goto="__end__",
            )

        except Exception as e:
            logger.exception("Error al renderizar el reporte de validación")
            return Command(
                update={
                    "messages": [
                        HumanMessage(
                            content=f"Error al renderizar el reporte: {e}",
                            name="render_validation_report",
                        )
                    ]
                },
                goto="__end__",
            )