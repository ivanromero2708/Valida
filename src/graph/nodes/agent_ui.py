from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
import logging
import os
from typing import Any, Literal, Iterable
from langsmith import traceable
from pydantic import ValidationError

from src.config.template_config import TEMPLATE_SETS
from src.config.configuration import Configuration
from src.graph.state import (
    ValidaState,
    FileDescriptor,
    DocumentGroupName,
    DocumentName,
)
from src.prompts.prompts_agent_ui import HUMAN_MESSAGE_PROMPT

logger = logging.getLogger(__name__)

multiagent_configuration = Configuration()
template_sets = TEMPLATE_SETS


DOC_KEY_TO_GROUP: dict[str, tuple[DocumentGroupName, DocumentName]] = {
    "dir_protocolo": (DocumentGroupName.PROTOCOLO, DocumentName.PROTOCOLO),
    "dir_hoja_trabajo_preparacion": (
        DocumentGroupName.HOJAS_TRABAJO_PREPARACION,
        DocumentName.HOJAS_TRABAJO_PREPARACION,
    ),
    "dirs_bitacora_preparacion": (
        DocumentGroupName.PREPARACION_BITACORAS,
        DocumentName.PREPARACION_BITACORAS,
    ),
    "dir_reporte_lims_linealidad": (
        DocumentGroupName.LINEALIDAD,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_linealidad": (
        DocumentGroupName.LINEALIDAD,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_linealidad": (
        DocumentGroupName.LINEALIDAD,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_linealidad": (
        DocumentGroupName.LINEALIDAD,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_precision_sistema": (
        DocumentGroupName.PRECISION_SISTEMA,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_precision_sistema": (
        DocumentGroupName.PRECISION_SISTEMA,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_precision_sistema": (
        DocumentGroupName.PRECISION_SISTEMA,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_precision_sistema": (
        DocumentGroupName.PRECISION_SISTEMA,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_precision_metodo": (
        DocumentGroupName.PRECISION_METODO,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_precision_metodo": (
        DocumentGroupName.PRECISION_METODO,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_precision_metodo": (
        DocumentGroupName.PRECISION_METODO,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_precision_metodo": (
        DocumentGroupName.PRECISION_METODO,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_precision_intermedia": (
        DocumentGroupName.PRECISION_INTERMEDIA,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_precision_intermedia": (
        DocumentGroupName.PRECISION_INTERMEDIA,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_precision_intermedia": (
        DocumentGroupName.PRECISION_INTERMEDIA,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_precision_intermedia": (
        DocumentGroupName.PRECISION_INTERMEDIA,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_exactitud": (
        DocumentGroupName.EXACTITUD,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_exactitud": (
        DocumentGroupName.EXACTITUD,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_exactitud": (
        DocumentGroupName.EXACTITUD,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_exactitud": (
        DocumentGroupName.EXACTITUD,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_estabilidad_solucion": (
        DocumentGroupName.ESTABILIDAD_SOLUCION,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_estabilidad_solucion": (
        DocumentGroupName.ESTABILIDAD_SOLUCION,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_estabilidad_solucion": (
        DocumentGroupName.ESTABILIDAD_SOLUCION,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_estabilidad_solucion": (
        DocumentGroupName.ESTABILIDAD_SOLUCION,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_estabilidad_solucion_fase_movil": (
        DocumentGroupName.ESTABILIDAD_FASE_MOVIL,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_estabilidad_solucion_fase_movil": (
        DocumentGroupName.ESTABILIDAD_FASE_MOVIL,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_estabilidad_solucion_fase_movil": (
        DocumentGroupName.ESTABILIDAD_FASE_MOVIL,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_estabilidad_solucion_fase_movil": (
        DocumentGroupName.ESTABILIDAD_FASE_MOVIL,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
    "dir_reporte_lims_robustez": (
        DocumentGroupName.ROBUSTEZ,
        DocumentName.REPORTE_LIMS,
    ),
    "dirs_hoja_trabajo_robustez": (
        DocumentGroupName.ROBUSTEZ,
        DocumentName.HOJAS_TRABAJO,
    ),
    "dirs_bitacoras_robustez": (
        DocumentGroupName.ROBUSTEZ,
        DocumentName.BITACORAS,
    ),
    "dirs_soportes_cromatograficos_robustez": (
        DocumentGroupName.ROBUSTEZ,
        DocumentName.SOPORTES_CROMATOGRAFICOS,
    ),
}


def _normalize_to_descriptors(value: Any) -> list[FileDescriptor]:
    descriptors: list[FileDescriptor] = []
    if value is None:
        return descriptors

    if isinstance(value, FileDescriptor):
        descriptors.append(value)
        return descriptors

    if isinstance(value, dict):
        try:
            descriptors.append(FileDescriptor(**value))
        except ValidationError as exc:
            logger.warning("No se pudo normalizar descriptor desde dict: %s", exc)
        return descriptors

    if isinstance(value, (list, tuple, set)):
        for item in value:
            descriptors.extend(_normalize_to_descriptors(item))
        return descriptors

    if isinstance(value, str):
        name = os.path.basename(value) or value
        descriptors.append(
            FileDescriptor(
                name=name,
                url=value,
                size=-1,
                content_type="application/octet-stream",
            )
        )
        return descriptors

    logger.debug("Valor ignorado al normalizar descriptor: %s", type(value))
    return descriptors


class AgentUI:
    """Agent UI that classifies validation documents and manages workflow"""

    def __init__(self):
        self.human_message_prompt = HUMAN_MESSAGE_PROMPT
        self.template_sets = TEMPLATE_SETS

    @traceable
    def _state_get(self, state: ValidaState, key: str, default: Any = "") -> Any:
        if isinstance(state, dict):
            return state.get(key, default)
        return getattr(state, key, default)

    @traceable
    def _collect_from_state(self, state: ValidaState, key: str) -> Iterable[FileDescriptor]:
        mapping = DOC_KEY_TO_GROUP.get(key)
        if mapping and hasattr(state, "get_files"):
            group, document = mapping
            try:
                return [descriptor.model_copy() for descriptor in state.get_files(group, document, allow_empty=True)]
            except ValueError as exc:
                logger.debug("Grupo no encontrado para %s: %s", key, exc)
        value = self._state_get(state, key, None)
        return [descriptor.model_copy() for descriptor in _normalize_to_descriptors(value)]

    @traceable
    def build_documents(self, state: ValidaState, set_name: str) -> list[FileDescriptor]:
        cfg = self.template_sets.get(set_name, {})
        keys: list[str] = cfg.get("doc_path_list", [])
        documents: list[FileDescriptor] = []
        seen: set[tuple[str, str]] = set()

        for key in keys:
            for descriptor in self._collect_from_state(state, key):
                dedup_key = (descriptor.url, descriptor.name)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                documents.append(descriptor)
        return documents

    @traceable
    def run(self, state: ValidaState, config: RunnableConfig) -> Command[Literal["index_node"]]:
        return Command(
            update={
                "messages": [HumanMessage(content="Inicio de proceso de investigación en documentos entregados.")],
            },
            goto=[
                Send(
                    "index_node",
                    {
                        "set_name": set_name,
                        "documents": self.build_documents(state, set_name),
                        "data_extraction_model": self.template_sets[set_name]["data_extraction_model"],
                        "tags": self.template_sets[set_name]["tags"],
                    },
                )
                for set_name in self.template_sets.keys()
            ],
        )
