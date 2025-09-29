# src/config/configuration.py
from typing import Annotated, Literal, List
from pydantic import BaseModel, Field
from src.config.prompts import (
    document_research_supervisor_system_prompt,
    index_prompt,
    structured_extraction_prompt,
    reasoning_prompt,
)

class Configuration(BaseModel):
    # Reasoning agent
    reasoning_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4o-mini",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "openai/gpt-5-mini",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["reasoning_agent"]},
    )
    
    reasoning_prompt: str = Field(
        default=reasoning_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["reasoning_agent"]},
    )
    
    reasoning_tools: List[Literal[
        "linearidad_tool",
    ]] = Field(
        default=["linearidad_tool"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["reasoning_agent"]},
    )
