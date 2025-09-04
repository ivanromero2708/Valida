from src.graph.state import ValidaState
from langgraph.graph import StateGraph

from src.graph.nodes import (
    AgentUI,
    SupervisorResearchValidation,
    RenderValidationReport
)

# Define the graph
valida_builder = StateGraph(ValidaState)

# Add nodes
valida_builder.add_node("agent_ui", AgentUI().run)
valida_builder.add_node("supervisor_research_validation", SupervisorResearchValidation().run)
valida_builder.add_node("render_validation_report", RenderValidationReport().run)

# Set entry point
valida_builder.set_entry_point("agent_ui")

# Compile the graph
valida_graph = valida_builder.compile()
