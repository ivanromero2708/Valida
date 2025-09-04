from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from src.graph.nodes.supervisor_research_validation.state import SupervisorResearchValidationOutput
from typing import Annotated, List
from pydantic import Field

class ValidaState(AgentStateWithStructuredResponse):
    """Estado del Sistema Agentico Valida"""
    context_for_render: Annotated[List[SupervisorResearchValidationOutput], Field(default_factory=list)]
    