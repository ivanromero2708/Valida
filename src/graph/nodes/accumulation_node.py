from langgraph.types import Command
from typing import Literal
import logging
from src.graph.state import ValidaState
from langchain_core.messages import HumanMessage

class AccumulationNode:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run(self, state: ValidaState) -> Command[Literal["agent_ui", "__end__"]]:
        status = state.get("op", "stage")
        
        if status == "stage":
            return Command(
                update={
                    "messages": [HumanMessage(content="Procesando documentos...")],
                },
                goto="__end__"
            )
        
        return Command(
            update={
                "messages": [HumanMessage(content="Procesamiento completado.")],
            },
            goto="agent_ui"
        )