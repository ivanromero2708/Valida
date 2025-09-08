from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage

from src.graph.nodes.supervisor_research_validation.state import SupervisorResearchValidationState
from src.agents.create_supervisor import make_supervisor
from src.agents.create_react_agent import make_react_agent
from src.config.configuration import Configuration

from typing import Literal

class SupervisorResearchValidation:
    def __init__(self):
        self.multiagent_configuration = Configuration()
    
    async def build_document_research_supervisor(self, state: SupervisorResearchValidationState, config_overrides: dict | None = None):
        
        data_extraction_model = state.get("data_extraction_model_key", None)
        data_rendering_model = state.get("data_rendering_model_key", None)
        structured_output_supervisor = state.get("structured_output_supervisor", None)
        
        loader_agent = await make_react_agent(
            RunnableConfig(
                configurable={
                    "name": "loader_agent",
                    "model": config_overrides.get("loader_llm", self.multiagent_configuration.loader_llm),
                    "system_prompt": config_overrides.get("loader_prompt", self.multiagent_configuration.loader_prompt),
                    "selected_tools": config_overrides.get("loader_tools", self.multiagent_configuration.loader_tools),
                }
            ),
            compile= True                        
        )
        
        vectorstore_agent= await make_react_agent(
            RunnableConfig(
                configurable={
                    "name": "vectorstore_agent",
                    "model": config_overrides.get("vectorstore_llm", self.multiagent_configuration.vectorstore_llm),
                    "system_prompt": config_overrides.get("vectorstore_prompt", self.multiagent_configuration.vectorstore_prompt),
                    "selected_tools": config_overrides.get("vectorstore_tools", self.multiagent_configuration.vectorstore_tools),
                }
            ),
            compile= True                        
        )
        
        structured_extraction_agent= await make_react_agent(
            RunnableConfig(
                configurable={
                    "name": "structured_extraction_agent",
                    "model": config_overrides.get("structured_extraction_llm", self.multiagent_configuration.structured_extraction_llm),
                    "system_prompt": config_overrides.get("structured_extraction_prompt", self.multiagent_configuration.structured_extraction_prompt),
                    "selected_tools": config_overrides.get("structured_extraction_tools", self.multiagent_configuration.structured_extraction_tools),
                }
            ),
            response_format = data_extraction_model,
            compile= True                        
        )
        
        reasoning_agent= await make_react_agent(
            RunnableConfig(
                configurable={
                    "name": "reasoning_agent",
                    "model": config_overrides.get("reasoning_llm", self.multiagent_configuration.reasoning_llm),
                    "system_prompt": config_overrides.get("reasoning_prompt", self.multiagent_configuration.reasoning_prompt),
                    "selected_tools": config_overrides.get("reasoning_tools", self.multiagent_configuration.reasoning_tools),
                }
            ),
            compile= True                        
        )
        
        render_agent= await make_react_agent(
            RunnableConfig(
                configurable={
                    "name": "render_agent",
                    "model": config_overrides.get("render_llm", self.multiagent_configuration.render_llm),
                    "system_prompt": config_overrides.get("render_prompt", self.multiagent_configuration.render_prompt),
                    "selected_tools": config_overrides.get("render_tools", self.multiagent_configuration.render_tools),
                }
            ),
            response_format = data_rendering_model,
            compile= True                        
        )
        
        # Supervisor
        document_research_supervisor = await make_supervisor(
            agents=[loader_agent, vectorstore_agent, structured_extraction_agent, reasoning_agent, render_agent],
            state_schema=SupervisorResearchValidationState,
            response_format = structured_output_supervisor,
            config=RunnableConfig(
                configurable={
                    "supervisor_name": "document_research_supervisor",
                    "supervisor_model": config_overrides.get("document_research_supervisor_llm", self.multiagent_configuration.document_research_supervisor_llm),
                    "supervisor_system_prompt": config_overrides.get("document_research_supervisor_system_prompt", self.multiagent_configuration.document_research_supervisor_system_prompt)
                }
            ),
            compile= False
        )
        
        return document_research_supervisor
    
    async def run(self, state: SupervisorResearchValidationState, config_overrides: dict | None = None) -> Command[Literal["render_validation_report"]]:
        supervisor = await self.build_document_research_supervisor(state, config_overrides)
        compiled_supervisor = supervisor.compile()
        
        response = await compiled_supervisor.ainvoke(
            {
                "messages": state.get("messages", []),
                "doc_path_list": state.get("doc_path_list", []),
                "data_extraction_model_key": state.get("data_extraction_model_key", None),
                "data_rendering_model_key": state.get("data_rendering_model_key", None),
                "structured_output_supervisor": state.get("structured_output_supervisor", None),
            }
        )
        
        context_for_render = response["structured_response"]
        
        return Command(
            update= {
                "messages": response.get("messages", []),
                "context_for_render": [context_for_render]
            },
            goto = "render_validation_report"
        )