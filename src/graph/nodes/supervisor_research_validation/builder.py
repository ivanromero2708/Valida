from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from src.graph.nodes.supervisor_research_validation.state import SupervisorResearchValidationState
from src.graph.state import SupervisorResearchValidationOutput
from src.agents.create_supervisor import make_supervisor
from src.agents.create_react_agent import make_react_agent
from src.config.configuration import Configuration


from typing import Literal

multiagent_configuration = Configuration()

class SupervisorResearchValidation:
    def __init__(self):
        self.multiagent_configuration = multiagent_configuration
    
    async def create_document_research_subagents(self, configurable: dict = None):
        """Crear todos los subagentes usando el patrón make_graph del repositorio oficial."""
        
        # Usar valores configurables si se proporcionan, sino usar defaults
        if configurable is None:
            configurable = {}
        
        # Crear index agent
        index_config = RunnableConfig(
            configurable={
                "model": configurable.get("index_llm", multiagent_configuration.index_llm),
                "system_prompt": configurable.get("index_prompt", multiagent_configuration.index_prompt),
                "selected_tools": configurable.get("index_tools", multiagent_configuration.index_tools),
                "name": "index_agent"
            }
        )
        index_agent = await make_react_agent(index_config)
        
        # Crear structured extraction agent
        structured_extraction_config = RunnableConfig(
            configurable={
                "model": configurable.get("structured_extraction_llm", multiagent_configuration.structured_extraction_llm),
                "system_prompt": configurable.get("structured_extraction_prompt", multiagent_configuration.structured_extraction_prompt),
                "selected_tools": configurable.get("structured_extraction_tools", multiagent_configuration.structured_extraction_tools),
                "name": "structured_extraction_agent"
            }
        )
        structured_extraction_agent = await make_react_agent(
            structured_extraction_config, 
            #response_format=configurable.get("data_extraction_model", None)
        )
        
        # Crear reasoning agent
        reasoning_config = RunnableConfig(
            configurable={
                "model": configurable.get("reasoning_llm", multiagent_configuration.reasoning_llm),
                "system_prompt": configurable.get("reasoning_prompt", multiagent_configuration.reasoning_prompt),
                "selected_tools": configurable.get("reasoning_tools", multiagent_configuration.reasoning_tools),
                "name": "reasoning_agent"
            }
        )
        reasoning_agent = await make_react_agent(reasoning_config)
        
        return [index_agent, structured_extraction_agent, reasoning_agent]

    # Función principal de construcción del supervisor siguiendo el patrón oficial
    async def make_document_research_supervisor(self, config: RunnableConfig):
        """Construir supervisor de investigación de documentos siguiendo el patrón oficial."""
            
        # Extraer valores de configuración directamente del config
        configurable = config.get("configurable", {})
        supervisor_model = configurable.get("document_research_supervisor_llm", multiagent_configuration.document_research_supervisor_llm)
        supervisor_system_prompt = configurable.get("document_research_supervisor_system_prompt", multiagent_configuration.document_research_supervisor_system_prompt)
            
        # Crear subagentes usando la función async, pasando valores configurables
        subagents = await self.create_document_research_subagents(configurable)

        # Crear supervisor
        supervisor_graph = await make_supervisor(
            agents=subagents,
            config=RunnableConfig(
                configurable={
                    "supervisor_name": "document_research_supervisor",
                    "supervisor_model": supervisor_model,
                    "supervisor_system_prompt": supervisor_system_prompt
                }
            ),
            state_schema=SupervisorResearchValidationState,
            response_format=configurable.get("structured_output_supervisor", None),
            compile=False
        )

        return supervisor_graph
    
    async def run(self, state: SupervisorResearchValidationState, config: RunnableConfig) -> Command[Literal["render_validation_report"]]:
        # Crear configuración con los parámetros del estado
        supervisor_config = RunnableConfig(
            configurable={
                "data_extraction_model": state.get("data_extraction_model", None),
                "structured_output_supervisor": state.get("structured_output_supervisor", None),
                # Agregar otros parámetros de configuración desde el config original
                **config.get("configurable", {})
            }
        )
        
        supervisor = await self.make_document_research_supervisor(supervisor_config)
        compiled_supervisor = supervisor.compile()
            
        response = await compiled_supervisor.ainvoke(
            {
                "messages": state.get("messages", []),
                "doc_path_list": state.get("doc_path_list", []),
                "data_extraction_model": state.get("data_extraction_model", None),
                "structured_output_supervisor": state.get("structured_output_supervisor", None),
            }
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

