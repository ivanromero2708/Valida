from src.graph.state import ValidaState
from langgraph.graph import StateGraph

from src.graph.nodes import (
    AgentUI,
    AnalyticalChemReasoning,
    RenderValidationReport,
    IndexNode,
    OPReasoningParallelization,
    AccumulationNode
)

# Define the graph
valida_builder = StateGraph(ValidaState)

# Add nodes
#valida_builder.add_node("accumulation_node", AccumulationNode().run)
valida_builder.add_node("agent_ui", AgentUI().run)
valida_builder.add_node("index_node", IndexNode().run)
valida_builder.add_node("op_reasoning_parallelization", OPReasoningParallelization().run)
valida_builder.add_node("analytical_chemistry_reasoning", AnalyticalChemReasoning().run)
valida_builder.add_node("render_validation_report", RenderValidationReport().run)

# Set entry point
valida_builder.set_entry_point("agent_ui")

# Compile the graph
valida_graph = valida_builder.compile()
