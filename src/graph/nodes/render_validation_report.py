from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage

from src.graph.state import ValidaState

class RenderValidationReport:
    def __init__(self):
        pass
    
    def run(self, state: ValidaState, config: RunnableConfig):
        configurable = config.get("configurable", {})        
                
        return Command(
            update= {
                "messages": [
                    SystemMessage(content="")
                ]
            },
            goto = "__end__"
        )