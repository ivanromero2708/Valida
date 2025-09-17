"""
Factory: build a LangGraph Supervisor over a set of sub-agents.

This wrapper uses `langgraph_supervisor.create_supervisor` and supports:
- Dependency injection for your chat model loader
- Optional state schema & response model
- Optional post_model_hook to project structured outputs into state
- Returns a compiled graph by default (toggle with compile=False)

Usage (async):
    from langchain_core.runnables import RunnableConfig
    from create_supervisor import make_supervisor

    sup_cfg = RunnableConfig(configurable={
        "supervisor_model": "openai/gpt-4.1-mini",
        "supervisor_system_prompt": "You are the coordinator. Call agents and consolidate.",
        "name": "patent_supervisor"
    })
    compiled_supervisor = await make_supervisor(
        agents=[agent_a, agent_b, agent_c],
        config=sup_cfg,
        # response_format=SomePydanticModel,  # optional
        # state_schema=SomeTypedDict,         # optional
    )
"""

from __future__ import annotations
from typing import Any, Callable, Optional, Sequence, Annotated

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict, NotRequired
from langgraph.graph.message import add_messages

# The reference package used in your snippet:
#   from langgraph_supervisor import create_supervisor
try:
    from langgraph_supervisor import create_supervisor
except Exception as e:
    raise ImportError(
        "Could not import `create_supervisor` from `langgraph_supervisor`. "
        "Install/enable the package or adjust the import as needed."
    ) from e

# Optional: load .env if present
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


class MinimalSupervisorState(TypedDict, total=False):
    """
    Minimal state for a LangGraph supervisor. You can pass your own TypedDict via
    `state_schema` if you need extra fields.
    """
    messages: Annotated[Sequence[AnyMessage], add_messages]


def _auto_load_chat_model() -> Callable[[str], object]:
    """Auto-import your project's model loader if available."""
    try:
        from src.utils.serialization_utils import load_chat_model as _load_chat_model  # type: ignore
    except Exception as e:
        raise ImportError(
            "Could not import load_chat_model from src.utils.serialization_utils. "
            "Pass `load_chat_model_fn` explicitly to make_supervisor(...)."
        ) from e
    return _load_chat_model


def _auto_context_schema():
    """Auto-import your Configuration class if available; otherwise return None."""
    try:
        from src.config.configuration import Configuration as _Configuration  # type: ignore

        return _Configuration
    except Exception:
        return None


async def make_supervisor(
    agents,
    config: RunnableConfig,
    *,
    load_chat_model_fn: Optional[Callable[[str], object]] = None,
    state_schema: Optional[type] = None,
    response_format: Optional[type] = None,
    context_schema: Optional[type] = None,
    output_mode: str = "last_message",
    compile: bool = True,
):
    supervisor_config = config.get("configurable", {})
    supervisor_model = supervisor_config.get("supervisor_model", "openai/gpt-4.1-mini")
    supervisor_system_prompt = supervisor_config.get(
        "supervisor_system_prompt", "You are a helpful coordinator."
    )
    # ✅ preferir 'supervisor_name', pero soportar 'name' por compatibilidad
    supervisor_name = supervisor_config.get("supervisor_name") or supervisor_config.get("name", "supervisor")

    load_chat_model_fn = load_chat_model_fn or _auto_load_chat_model()
    state_schema = state_schema or MinimalSupervisorState
    context_schema = context_schema if context_schema is not None else _auto_context_schema()

    supervisor = create_supervisor(
        agents=agents,
        model=load_chat_model_fn(supervisor_model),
        prompt=supervisor_system_prompt,
        state_schema=state_schema,
        response_format=response_format,
        context_schema=context_schema,
        output_mode=output_mode,
        # ⬇️ ⬇️  cambio clave
        supervisor_name=supervisor_name,
    )
    
    # Add name attribute to the supervisor for langgraph_supervisor compatibility
    supervisor.name = supervisor_name
    
    return supervisor.compile() if compile else supervisor

