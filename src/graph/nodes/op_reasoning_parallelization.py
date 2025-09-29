
from langchain_core.messages import HumanMessage
from langgraph.types import Command, Send
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
import logging
from typing import Any, Literal
from langsmith import traceable
from src.config.template_config import TEMPLATE_SETS
from src.config.configuration import Configuration
from src.prompts.prompts_agent_ui import HUMAN_MESSAGE_PROMPT
from src.graph.state import ValidaState
import json

logger = logging.getLogger(__name__)

multiagent_configuration = Configuration()
template_sets = TEMPLATE_SETS

from langsmith import traceable

class OPReasoningParallelization:
    def __init__(self):
        self.human_message_prompt = HUMAN_MESSAGE_PROMPT
        self.template_sets = TEMPLATE_SETS
    
    @traceable
    def _get_context_data_json_str(self, state: ValidaState, set_name: str) -> str:
        """
        Soporta tres formas de state["extraction_content"]:
        1) dict[str, Any]  -> { "Set 2": [...], "Set 3": [...] }
        2) list[dict]      -> [ {"set_name": "Set 2", "extracted_content": [...]}, ... ]
        3) objeto          -> con attrs .set_name y .extracted_content
        Devuelve un JSON (string) del contenido asociado al set.
        """
        ec = state.get("extraction_content")
        payload = None

        try:
            if not ec:
                payload = None
            elif isinstance(ec, dict):
                # si ya está indexado por set
                payload = ec.get(set_name)
            elif isinstance(ec, list):
                # lista de bloques por set
                for item in ec:
                    if isinstance(item, dict) and item.get("set_name") == set_name:
                        payload = item.get("extracted_content")
                        break
                    if hasattr(item, "set_name") and item.set_name == set_name:
                        payload = getattr(item, "extracted_content", None)
                        break
            else:
                # objeto con attrs
                if getattr(ec, "set_name", None) == set_name:
                    payload = getattr(ec, "extracted_content", None)
        except Exception as e:
            logger.exception("Fallo obteniendo extraction_content para %s: %s", set_name, e)
            payload = None

        if payload is None:
            return ""

        try:
            return json.dumps(payload)
        except TypeError:
            try:
                if hasattr(payload, "model_dump"):
                    return json.dumps(payload.model_dump())
                if isinstance(payload, list):
                    serializable = []
                    for item in payload:
                        if hasattr(item, "model_dump"):
                            serializable.append(item.model_dump())
                        else:
                            serializable.append(item)
                    return json.dumps(serializable)
            except Exception:
                pass

        return str(payload)
    
    @traceable
    def run(self, state: ValidaState) -> Command[Literal["analytical_chemistry_reasoning"]]:
        return Command(
            update= {
                "messages": [HumanMessage(content="Inicio de proceso de investigación en documentos entregados.")],
            },
            goto = [
                Send(
                    "analytical_chemistry_reasoning",
                    {
                        "messages": [
                                HumanMessage(
                                    content= self.human_message_prompt.format(
                                    reglas_razonamiento=template_sets[set_name]["human_message_prompt"],
                                    tags=template_sets[set_name]["tags"],
                                    context_data_json_str=self._get_context_data_json_str(state, set_name),
                                    structured_output_supervisor=template_sets[set_name]["structured_output_supervisor"],
                                )
                            )
                        ],
                    "structured_output_supervisor": template_sets[set_name]["structured_output_supervisor"],
                    "tags": template_sets[set_name]["tags"],
                    "set_name": set_name,
                }
            )
            for set_name in self.template_sets.keys()
        ]
    )