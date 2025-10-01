"""Renderizador de reportes de validaciÃ³n para el sistema Valida."""

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
from src.utils.pathing import get_images_root, resolve_input_path

try:
    from docxtpl import DocxTemplate, InlineImage
    from docx.shared import Mm
    from jinja2.exceptions import UndefinedError
except ImportError:
    DocxTemplate = None
    InlineImage = None
    Mm = None
    UndefinedError = None
    logging.warning("docxtpl not installed. DOCX rendering will not be available.")

logger = logging.getLogger(__name__)

_BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = _BASE_DIR / "templates" / "validation_template20250916.docx"
OUTPUT_DIR = _BASE_DIR / "output"
IMAGES_ROOT = get_images_root()

class RenderValidationReport:
    """Renderiza reportes de validaciÃ³n en plantillas DOCX para el sistema Valida."""

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
        """Limpia texto para evitar caracteres no vÃ¡lidos en DOCX y normaliza Unicode."""
        if text is None:
            return ""
        if not isinstance(text, str):
            text = str(text)
        # Normaliza Unicode
        text = unicodedata.normalize("NFC", text)
        # Remueve caracteres de control no permitidos por docx
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
        # Normaliza saltos de lÃ­nea
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Colapsa espacios repetidos (no toca saltos de lÃ­nea)
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
        """FusiÃ³n simple: las claves de extra sobrescriben base."""
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
        Esto evita romper por claves faltantes en plantillas muy grandes/dinÃ¡micas.
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
                    logger.warning(f"Variable faltante en plantilla: '{missing}'. Se rellenarÃ¡ con ''. (Intento {attempt})")
                    context.setdefault(missing, "")
                else:
                    # Si no se pudo extraer, abortamos para no ciclar
                    raise

    def _resolve_image_path(self, raw: Optional[str | Path]) -> tuple[Optional[str], Optional[Path], Optional[Path]]:
        """Normaliza la ruta de imagen y devuelve original, normalizada y existente."""
        if not raw:
            return None, None, None

        raw_str = str(raw)
        normalised = resolve_input_path(raw_str, data_root=IMAGES_ROOT)
        if normalised and normalised.exists():
            return raw_str, normalised, normalised

        candidate = Path(raw_str)
        if candidate.exists():
            return raw_str, normalised, candidate

        return raw_str, normalised, None



    def _process_activos_images(self, doc: DocxTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y normaliza las imÃ¡genes de los activos de linealidad."""
        if InlineImage is None or Mm is None:
            logger.warning("InlineImage o Mm no disponibles. Las imÃ¡genes no se procesarÃ¡n.")
            return context

        activos_linealidad = context.get("activos_linealidad", [])
        if not activos_linealidad:
            logger.info("No se encontraron activos_linealidad en el contexto.")
            return context

        processed_activos: list[dict[str, Any]] = []

        for i, activo in enumerate(activos_linealidad):
            if not isinstance(activo, dict):
                logger.warning("Activo %s no es un diccionario, se omite.", i + 1)
                processed_activos.append(activo)
                continue

            activo_copy = dict(activo)
            nombre_activo = activo_copy.get("nombre", f"Activo_{i + 1}")

            original_reg, normalised_reg, resolved_reg = self._resolve_image_path(activo_copy.get("regresion_png_path"))
            if resolved_reg:
                try:
                    activo_copy["regresion_png_path"] = InlineImage(
                        doc,
                        image_descriptor=str(resolved_reg),
                        width=Mm(120),
                        height=Mm(80),
                    )
                    logger.info("Imagen de regresiÃ³n agregada para %s: %s", nombre_activo, resolved_reg)
                except Exception as exc:
                    logger.warning("Error al agregar imagen de regresiÃ³n para %s (%s): %s", nombre_activo, resolved_reg, exc)
                    activo_copy["regresion_png_path"] = ""
            else:
                logger.warning(
                    "Imagen de regresiÃ³n no encontrada para %s: original=%s, normalizada=%s",
                    nombre_activo,
                    original_reg,
                    normalised_reg,
                )
                activo_copy["regresion_png_path"] = ""

            original_res, normalised_res, resolved_res = self._resolve_image_path(activo_copy.get("residuales_png_path"))
            if resolved_res:
                try:
                    activo_copy["residuales_png_path"] = InlineImage(
                        doc,
                        image_descriptor=str(resolved_res),
                        width=Mm(120),
                        height=Mm(80),
                    )
                    logger.info("Imagen de residuales agregada para %s: %s", nombre_activo, resolved_res)
                except Exception as exc:
                    logger.warning("Error al agregar imagen de residuales para %s (%s): %s", nombre_activo, resolved_res, exc)
                    activo_copy["residuales_png_path"] = ""
            else:
                logger.warning(
                    "Imagen de residuales no encontrada para %s: original=%s, normalizada=%s",
                    nombre_activo,
                    original_res,
                    normalised_res,
                )
                activo_copy["residuales_png_path"] = ""

            processed_activos.append(activo_copy)

        context["activos_linealidad"] = processed_activos
        logger.info("Procesadas imÃ¡genes para %s activos.", len(processed_activos))
        return context




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
        Ejecuta el renderizado del reporte de validaciÃ³n.

        Returns:
            Command con estado actualizado y finalizaciÃ³n del flujo.
        """
        # Verificar disponibilidad de la librerÃ­a
        if DocxTemplate is None:
            logger.error("docxtpl no estÃ¡ instalado. No es posible renderizar el DOCX.")
            return Command(
                update={
                    "messages": [
                        HumanMessage(
                            content="No se pudo generar el reporte: falta la librerÃ­a docxtpl.",
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

        # 2) Agregar informaciÃ³n bÃ¡sica del estado
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

        # 4) Combinar y limpiar texto
        final_context = self._merge_contexts(basic_context, tags_map)
        
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
                            content=f"No se encontrÃ³ la plantilla en {tpl_path}",
                            name="render_validation_report",
                        )
                    ]
                },
                goto="__end__",
            )

        # 6) Renderizar y guardar
        try:
            doc = DocxTemplate(str(tpl_path))
            
            # 5) Procesar imÃ¡genes de linealidad para cada activo
            final_context = self._process_activos_images(doc, final_context)
            
            # Intento robusto ante variables faltantes
            if UndefinedError is not None:
                self._render_with_fallback_missing(doc, final_context, max_retries=50)
            else:
                doc.render(final_context)

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname_out = OUTPUT_DIR / f"validation_report_{timestamp}.docx"
            doc.save(str(fname_out))

            msg = f"Reporte de validaciÃ³n generado en: {fname_out}"
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
            logger.exception("Error al renderizar el reporte de validaciÃ³n")
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
