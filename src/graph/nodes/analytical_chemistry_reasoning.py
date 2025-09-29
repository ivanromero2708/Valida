from langgraph.types import Command
from typing import Literal, List
from langchain_core.messages import HumanMessage
from langgraph.prebuilt.chat_agent_executor import AgentStateWithStructuredResponse
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from src.agents.create_react_agent import make_react_agent
from src.config.configuration import Configuration
from src.graph.nodes.supervisor_research_validation.builder import SupervisorResearchValidationOutput

multiagent_configuration = Configuration()

class AnalyticalChemReasoningState(AgentStateWithStructuredResponse):
    set_name: str
    structured_output_supervisor: type[BaseModel]
    tags: list[str]
    context_for_render: List[SupervisorResearchValidationOutput]


class AnalyticalChemReasoning:
    def __init__(self):
        pass
    
    async def _create_reasoning_agent(self, state: AnalyticalChemReasoningState, configurable: dict = None):
        if configurable is None:
            configurable = {}
        
        structured_output_supervisor = state.get("structured_output_supervisor", None)
        
        reasoning_config = RunnableConfig(
            configurable={
                "model": configurable.get("reasoning_llm", multiagent_configuration.reasoning_llm),
                "system_prompt": configurable.get("reasoning_prompt", multiagent_configuration.reasoning_prompt),
                "selected_tools": configurable.get("reasoning_tools", multiagent_configuration.reasoning_tools),
                "name": "reasoning_agent"
            }
        )
        reasoning_agent = await make_react_agent(
            reasoning_config, 
            response_format=structured_output_supervisor
        )
        return reasoning_agent
    
    async def run(self, state: AnalyticalChemReasoningState) -> Command[Literal["render_validation_report"]]:
        reasoning_agent = await self._create_reasoning_agent(state)
        
        response = await reasoning_agent.ainvoke(
            state
        )
        
        structured_response = response["structured_response"]
        
        # Convertir el objeto Pydantic a diccionario si es necesario
        if hasattr(structured_response, 'model_dump'):
            # Es un modelo Pydantic, convertir a dict
            context_data = structured_response.model_dump()
        elif hasattr(structured_response, 'dict'):
            # Versión anterior de Pydantic
            context_data = structured_response.dict()
        elif isinstance(structured_response, dict):
            # Ya es un diccionario
            context_data = structured_response
        else:
            # Fallback: intentar convertir a dict
            context_data = dict(structured_response) if structured_response else {}
            
        context_for_render = SupervisorResearchValidationOutput(
            set_name=state.get("set_name"),
            context_for_set=context_data,
        )
            
        final_messages = response["messages"]
            
        return Command(
            update= {
                "messages": [
                    HumanMessage(
                        content=final_messages[-1].content if final_messages else "Document research completed",
                    )
                ],
                "context_for_render": [context_for_render],
            },
            goto = "render_validation_report"
        )