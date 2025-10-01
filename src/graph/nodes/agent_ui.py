from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
import logging
from typing import Any, Literal
from langsmith import traceable

from src.config.template_config import TEMPLATE_SETS
from src.config.configuration import Configuration
from src.graph.state import ValidaState
from src.prompts.prompts_agent_ui import HUMAN_MESSAGE_PROMPT
from src.utils.pathing import resolve_input_path

logger = logging.getLogger(__name__)

multiagent_configuration = Configuration()
template_sets = TEMPLATE_SETS

def _coerce_to_list(value: Any) -> list[str]:
    """Convierte un valor potencialmente str/list/tuple/set en lista[str] sin vacíos."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value if v]
    return [str(value)] if value else []

class AgentUI:
    """Agent UI that classifies validation documents and manages workflow"""
    
    def __init__(self):
        self.human_message_prompt = HUMAN_MESSAGE_PROMPT
        # Mantener una referencia explícita en la instancia, según lo solicitado
        self.template_sets = TEMPLATE_SETS
    
    def _state_get(self, state: ValidaState, key: str, default: Any = "") -> Any:
        """Obtiene valores del state soportando dict o atributos."""
        if isinstance(state, dict):
            return state.get(key, default)
        else:
            return getattr(state, key, default)
    
    @traceable
    def build_doc_path_list(self, state: ValidaState, set_name: str) -> list[dict[str, str]]:
        cfg = self.template_sets.get(set_name, {})
        keys: list[str] = cfg.get("doc_path_list", [])
        paths: list[str] = []

        for k in keys:
            v = self._state_get(state, k, "")
            paths.extend(_coerce_to_list(v))

        seen: set[str] = set()
        unique_paths: list[str] = []
        for p in paths:
            p_str = str(p).strip()
            if p_str and p_str not in seen:
                seen.add(p_str)
                unique_paths.append(p_str)

        resolved_entries: list[dict[str, str]] = []
        for original_path in unique_paths:
            resolved_path = resolve_input_path(original_path)
            if resolved_path is None:
                logger.warning("Ruta no interpretable: %s", original_path)
                continue

            resolved_path = resolved_path.resolve()
            if not resolved_path.exists():
                logger.warning(
                    "Documento no encontrado tras normalizar '%s' -> '%s'",
                    original_path,
                    resolved_path,
                )
                continue

            resolved_entries.append(
                {
                    "original_path": str(original_path),
                    "resolved_path": str(resolved_path),
                }
            )

        if not resolved_entries:
            logger.warning("Set %s sin documentos tras normalizar rutas", set_name)

        return resolved_entries

    
    @traceable
    def run(self, state: ValidaState, config: RunnableConfig) -> Command[Literal["index_node"]]:
        return Command(
            update= {
                "messages": [HumanMessage(content="Inicio de proceso de investigación en documentos entregados.")],
            },
            goto = [
                Send(
                    "index_node",
                    {
                        "set_name": set_name,
                        "doc_path_list": self.build_doc_path_list(state, set_name),
                        "data_extraction_model": self.template_sets[set_name]["data_extraction_model"],
                        "tags": self.template_sets[set_name]["tags"],
                    }
                )
                for set_name in self.template_sets.keys()
            ]
        )

