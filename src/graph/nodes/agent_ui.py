from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

from src.graph.state import ValidaState
from pydantic import BaseModel

class AgentUIOutput(BaseModel):
    hand_off_to_research_supervisor: bool

class AgentUI:
    def __init__(self):
        pass
    
    def run(self, state: ValidaState, config: RunnableConfig):
        configurable = config.get("configurable", {})        
        template_sets = configurable.get("template_sets", {})
        
        # TODO Crear un LLM call para evaluar si los documentos ingresados son suficientes para iniciar el workflow
        # Si no son suficientes, enviar mensaje de respuesta indicando que hace falta.
        # Si son suficientes, continuar con el workflow.
        
        # Por ahora, simulamos la evaluación - en el futuro aquí irá la lógica del LLM
        response = AgentUIOutput(hand_off_to_research_supervisor=True)
        
        goto_parallelized = [
            Send(
                "supervisor_research_validation",
                {
                    "messages": [
                        HumanMessage(
                            content=template_sets[set_name]["human_message_prompt"],
                            name = f"Request from {set_name}"
                        )
                    ],
                    "doc_path_list": template_sets[set_name]["doc_path_list"],
                    "data_extraction_model_key": template_sets[set_name]["data_extraction_model_key"],
                    "data_rendering_model_key": template_sets[set_name]["data_rendering_model_key"],
                    "structured_output_supervisor": template_sets[set_name]["structured_output_supervisor"],
                }
            )
            for set_name in template_sets.keys()
        ]
        
        if response.hand_off_to_research_supervisor:
            goto = goto_parallelized
        else:
            goto = "__end__"
        
        return Command(
            update= {
                "messages": [
                    SystemMessage(content="Research sets selected successfully.")
                ]
            },
            goto = goto
        )