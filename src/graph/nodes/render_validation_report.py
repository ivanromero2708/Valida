"""Renderizador de reportes de validación para el sistema Valida."""

from pathlib import Path
from typing import Dict, Any, List, Literal
import logging
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command
from langchain_core.messages import HumanMessage

from src.graph.state import ValidaState

try:
    from docxtpl import DocxTemplate
except ImportError:
    DocxTemplate = None
    logging.warning("docxtpl not installed. DOCX rendering will not be available.")

logger = logging.getLogger(__name__)

class RenderValidationReport:
    """Renderiza reportes de validación en plantillas DOCX para el sistema Valida."""

    def __init__(self):
        # Ruta real del template en este repo
        self.template_path = "./src/templates/validation_template.docx"

    def _aggregate_context(self, context_list: List[Any]) -> Dict[str, Any]:
        """Aplana y unifica la lista de contextos por set (tag -> valor)."""
        aggregated: Dict[str, Any] = {}
        if not context_list:
            return aggregated
        
        for item in context_list:
            try:
                ctx = getattr(item, "context_for_set", {}) or {}
                if isinstance(ctx, dict):
                    aggregated.update(ctx)
            except Exception as e:
                logger.warning(f"Error procesando contexto: {e}")
                continue
        return aggregated

    def run(self, state: ValidaState, config: RunnableConfig) -> Command[Literal["__end__"]]:
        """
        Ejecuta el renderizado del reporte de validación.

        Args:
            state: Estado actual con tags acumulados
            config: Configuración de ejecución

        Returns:
            Command con estado actualizado y finalización del flujo
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

        # 1) Aplanar el contexto acumulado de todos los supervisores
        context_list = state.get("context_for_render", [])
        tags_map = self._aggregate_context(context_list)

        # 2) Agregar información básica del estado
        basic_context = {
            "validacion": state.get("validacion", ""),
            "codigo_informe": state.get("codigo_informe", ""),
            "nombre_producto": state.get("nombre_producto", ""),
            "codigo_producto": state.get("codigo_producto", ""),
            "rango_validado": state.get("rango_validado", ""),
            "fecha_render": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lista_activos": [
                {
                    "nombre": api.nombre,
                    "concentracion": api.concentracion
                }
                for api in state.get("lista_activos", [])
            ]
        }

        # 3) Combinar contexto básico con tags procesados
        final_context = {**basic_context, **tags_map}

        # 4) Renderizar y guardar
        tpl_path = Path(self.template_path)
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

        try:
            # Cargar plantilla y renderizar
            doc = DocxTemplate(str(tpl_path))
            doc.render(final_context)
            
            # Guardar archivo de salida
            out_dir = Path("output")
            out_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname_out = out_dir / f"validation_report_{timestamp}.docx"
            doc.save(str(fname_out))
            
            msg = f"Reporte de validación generado en: {fname_out}"
            logger.info(msg)
            
            return Command(
                update={
                    "messages": [HumanMessage(content=msg, name="render_validation_report")],
                    "fname_out": str(fname_out),
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