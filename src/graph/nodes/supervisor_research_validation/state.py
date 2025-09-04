from typing import Annotated, List, Dict, Any
import operator
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from pydantic import BaseModel, Field

class SupervisorResearchValidationOutput(BaseModel):
    set_name: str = Field(..., description="Name of the tag set")
    context_for_set: Dict[str, Any] = Field(..., description="Context for the tag set")

class SupervisorResearchValidationState(AgentStateWithStructuredResponse):
    doc_path_list: list[str]
    data_model_key: list[str]
    context_for_render: SupervisorResearchValidationOutput
