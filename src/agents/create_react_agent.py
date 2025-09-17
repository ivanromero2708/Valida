"""
Factory: build a LangGraph ReAct agent using langgraph.prebuilt.create_react_agent.

Usage (async):
    from langchain_core.runnables import RunnableConfig
    from create_react_agent import make_react_agent

    cfg = RunnableConfig(configurable={
        "model": "openai/gpt-4.1-mini",
        "selected_tools": ["get_todays_date"],
        "system_prompt": "You are a helpful assistant.",
        "name": "orange_book_researcher",
    })
    agent = await make_react_agent(cfg, compile=False)  # returns a graph (uncompiled by default)
    # compiled = agent.compile()
"""

from __future__ import annotations
from typing import Callable, Iterable, Optional

from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from src.config.configuration import Configuration
from src.tools.tools_registry import get_tools

from dotenv import load_dotenv

load_dotenv()

from src.config.configuration import Configuration
from src.utils.serialization_utils import load_chat_model

async def make_react_agent(
    config: RunnableConfig,
    *,
    load_chat_model_fn: Optional[Callable[[str], object]] = None,
    response_format: Optional[type] = None,
    config_schema: Optional[type] = None,
):
    """
    Build a single ReAct agent graph from a RunnableConfig.

    Parameters
    ----------
    config
        A RunnableConfig with a `configurable` dict supporting:
          - model: str (LLM id for your loader)
          - selected_tools: Iterable[str]
          - system_prompt: str
          - name: str
    get_tools_fn
        Callable that receives an iterable of tool names and returns tool instances.
        Defaults to src.tools.tools_registry.get_tools if available.
    load_chat_model_fn
        Callable that receives a model id string and returns an LCEL-compatible chat model.
        Defaults to src.utils.serialization_utils.load_chat_model if available.
    config_schema
        Optional schema class (e.g., your Configuration) to expose configurable params.
        If omitted, tries to import Configuration automatically; if not found, uses None.
    compile
        If True, returns a compiled graph; otherwise returns the uncompiled builder.

    Returns
    -------
    StateGraph | CompiledGraph
    """
    agent_config = config.get("configurable", {})
    llm_id = agent_config.get("model", "openai/gpt-4.1-mini")
    selected_tools = agent_config.get("selected_tools", ["get_todays_date"])
    system_prompt = agent_config.get("system_prompt", "You are a helpful assistant.")
    name = agent_config.get("name", "react_agent")

    load_chat_model_fn = load_chat_model
    config_schema = Configuration

    # Build
    graph = create_react_agent(
        model=load_chat_model_fn(llm_id),
        tools=get_tools(selected_tools),
        prompt=system_prompt,
        config_schema=config_schema,
        response_format= response_format,
        name=name,
    )
    
    # Add name attribute to the graph for langgraph_supervisor compatibility
    graph.name = name

    return graph
