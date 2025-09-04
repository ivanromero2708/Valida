from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage

from src.graph.nodes.supervisor_research_validation.state import SupervisorResearchValidationState

class SupervisorResearchValidation:
    def __init__(self):
        pass
    
    def run(self, state: SupervisorResearchValidationState, config: RunnableConfig):
        configurable = config.get("configurable", {})        
                
        return Command(
            update= {
                "messages": [
                    SystemMessage(content="")
                ],
                "context_for_render": []
            },
            goto = "render_validation_report"
        )