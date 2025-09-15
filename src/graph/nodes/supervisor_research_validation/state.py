from typing import Type, List
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from pydantic import BaseModel
from src.graph.state import SupervisorResearchValidationOutput

class SupervisorResearchValidationState(AgentStateWithStructuredResponse):
    set_name: str
    doc_path_list: List[str]
    data_extraction_model: Type[BaseModel]
    structured_output_supervisor: Type[BaseModel]
    tags: List[str]
    context_for_render: List[SupervisorResearchValidationOutput]
