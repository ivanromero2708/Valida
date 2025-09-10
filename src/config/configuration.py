# src/config/configuration.py
from typing import Annotated, Literal, List
from pydantic import BaseModel, Field
from src.config.prompts import (
    document_research_supervisor_system_prompt,
    loader_prompt,
    vectorstore_prompt,
    structured_extraction_prompt,
    reasoning_prompt,
    render_prompt,
)
from src.config.template_config import TEMPLATE_SETS
from typing import Dict, Any

class Configuration(BaseModel):
    # Template configuration
    template_sets: Dict[str, Any] = Field(default=TEMPLATE_SETS)
    
    # Supervisor document research
    document_research_supervisor_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["document_research_supervisor"]},
    )
    
    document_research_supervisor_system_prompt: str = Field(
        default=document_research_supervisor_system_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["document_research_supervisor"]},
    )
    
    # Document Loader agent
    loader_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["loader_agent"]},
    )
    
    loader_prompt: str = Field(
        default=loader_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["loader_agent"]},
    )
    
    loader_tools: List[Literal[
        "get_document_content",
    ]] = Field(
        default=["get_document_content"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["loader_agent"]},
    )
    
    # Vectorstore agent
    vectorstore_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["vectorstore_agent"]},
    )
    
    vectorstore_prompt: str = Field(
        default=vectorstore_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["vectorstore_agent"]},
    )
    
    vectorstore_tools: List[Literal[
        "add_document_to_vectorstore",
    ]] = Field(
        default=["add_document_to_vectorstore"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["vectorstore_agent"]},
    )
    
    # Structured extraction agent
    structured_extraction_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["structured_extraction_agent"]},
    )
    
    structured_extraction_prompt: str = Field(
        default=structured_extraction_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["structured_extraction_agent"]},
    )
    
    structured_extraction_tools: List[Literal[
        "extract_structured_data",
    ]] = Field(
        default=["extract_structured_data"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["structured_extraction_agent"]},
    )
    
    # Reasoning agent
    reasoning_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
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
        "reason_about_structured_data",
    ]] = Field(
        default=["reason_about_structured_data"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["reasoning_agent"]},
    )
    
    # Render agent
    render_llm: Annotated[
        Literal[
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-5-sonnet-latest",
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "openai/o3-mini",
            "openai/o4-mini",
            "openai/gpt-5",
            "google/gemini-2.0-flash-lite",
        ], 
        {"__template_metadata__": {"kind": "llm"}},
    ] = Field(
        default="openai/gpt-4.1-mini",
        description="El modelo de lenguaje a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["render_agent"]},
    )
    
    render_prompt: str = Field(
        default=render_prompt,
        description="El prompt a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["render_agent"]},
    )
    
    render_tools: List[Literal[
        "render_reasoning",
    ]] = Field(
        default=["render_reasoning"],
        description="Las herramientas a usar para el agente.",
        json_schema_extra={"langgraph_nodes": ["render_agent"]},
    )