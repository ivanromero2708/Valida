from __future__ import annotations

import json
from typing import Any
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage


def message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain ``BaseMessage`` into a plain Python ``dict``."""
    if isinstance(message, HumanMessage):
        msg_type = "human"
    elif isinstance(message, AIMessage):
        msg_type = "ai"
    elif isinstance(message, SystemMessage):
        msg_type = "system"
    else:
        msg_type = getattr(message, "type", "ai")

    data = {"type": msg_type, "content": message.content}
    if getattr(message, "name", None):
        data["name"] = message.name
    return data


def jsonify_safe(obj: Any) -> str:
    """Serialize ``obj`` to JSON, falling back to ``str`` on failure."""
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(obj)


"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)