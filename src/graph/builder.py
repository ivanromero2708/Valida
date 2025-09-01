from src.graph.state import ValidaState
from langgraph.graph import StateGraph
from src.graph.nodes.agent_ui import agent_ui
from src.graph.nodes.supervisor_research_validation.builder import supervisor_research_validation
from src.graph.nodes.render_validation_report import render_validation_report

# Define the graph
valida_builder = StateGraph(ValidaState)

# Add nodes
valida_builder.add_node(agent_ui)
valida_builder.add_node(supervisor_research_validation)
valida_builder.add_node(render_validation_report)

# Set entrypoint
valida_builder.set_entrypoint("agent_ui")

# Compile the graph
valida_graph = valida_builder.compile()
