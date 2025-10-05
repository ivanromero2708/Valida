from langgraph.types import Command, Send
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
import base64
import binascii
import hashlib
import logging
import os
from typing import Any, Iterable, Literal
from collections.abc import Mapping
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


def _clean_base64_payload(value: str) -> str:
    return "".join(value.strip().split())


def _extract_base64_from_value(value: str) -> tuple[str | None, str | None]:
    stripped = value.strip()
    if not stripped:
        return None, None
    if stripped.startswith("data:"):
        header, _, payload = stripped.partition(",")
        if ";base64" not in header:
            return None, None
        mime = header[5:].split(";")[0] or None
        return _clean_base64_payload(payload), mime
    if any(sep in stripped for sep in ("://", "\\", "/")):
        return None, None
    if len(stripped) < 128:
        return None, None
    try:
        base64.b64decode(stripped, validate=True)
    except (binascii.Error, ValueError):
        return None, None
    return _clean_base64_payload(stripped), None


def _estimate_base64_size(value: str) -> int:
    payload = _clean_base64_payload(value)
    padding = payload.count("=")
    length = len(payload)
    return max((length * 3) // 4 - padding, 0)


def _guess_extension(content_type: str | None) -> str:
    mapping = {
        "application/pdf": ".pdf",
        "image/png": ".png",
        "image/jpeg": ".jpg",
    }
    return mapping.get(content_type, ".bin")


def _descriptor_fingerprint(descriptor: FileDescriptor) -> str | None:
    if descriptor.source and descriptor.source.lower() == "sharepoint":
        if descriptor.unique_id:
            return f"sharepoint:{descriptor.unique_id}"
        if descriptor.site_lookup and descriptor.server_relative_path:
            return f"sharepoint:{descriptor.site_lookup}:{descriptor.server_relative_path}"
        if descriptor.server_relative_path:
            return f"sharepoint:{descriptor.server_relative_path}"
    if descriptor.url:
        return descriptor.url
    if descriptor.checksum:
        return f"checksum:{descriptor.checksum}"
    if descriptor.content_base64:
        digest = hashlib.sha1(descriptor.content_base64.encode("utf-8")).hexdigest()
        return f"base64:{digest}"
    return None


def _normalize_to_descriptors(value: Any) -> list[FileDescriptor]:
    descriptors: list[FileDescriptor] = []
    if value is None:
        return descriptors

    if isinstance(value, FileDescriptor):
        descriptors.append(value)
        return descriptors

    if isinstance(value, Mapping):
        data = dict(value)

        if not data.get("source") and (
            data.get("siteLookup")
            or data.get("siteUrl")
            or data.get("serverRelativePath")
            or data.get("uniqueId")
        ):
            data["source"] = "sharepoint"

        if "name" not in data:
            for candidate in ("filename", "file_name"):
                candidate_value = data.get(candidate)
                if isinstance(candidate_value, str) and candidate_value:
                    data["name"] = candidate_value
                    break

        url_value = data.get("url")
        if isinstance(url_value, str):
            payload, mime = _extract_base64_from_value(url_value)
            if payload:
                data.setdefault("content_base64", payload)
                data["url"] = None
                if mime and not data.get("content_type"):
                    data["content_type"] = mime

        base64_value = data.get("content_base64")
        if isinstance(base64_value, str):
            payload, mime = _extract_base64_from_value(base64_value)
            if payload:
                data["content_base64"] = payload
                if mime and not data.get("content_type"):
                    data["content_type"] = mime
                if not data.get("size"):
                    data["size"] = _estimate_base64_size(payload)
                if not data.get("checksum"):
                    data["checksum"] = hashlib.sha1(payload.encode("utf-8")).hexdigest()
                if not data.get("name"):
                    suffix = _guess_extension(
                        data.get("content_type") or "application/pdf"
                    )
                    data["name"] = f"document_{data['checksum'][:8]}{suffix}"

        if not data.get("size"):
            data["size"] = -1

        if not data.get("content_type"):
            content_type = None
            name = data.get("name")
            if isinstance(name, str):
                _, ext = os.path.splitext(name)
                ext = ext.lower()
                if ext == ".pdf":
                    content_type = "application/pdf"
                elif ext == ".png":
                    content_type = "image/png"
                elif ext in {".jpg", ".jpeg"}:
                    content_type = "image/jpeg"
            data["content_type"] = content_type or "application/octet-stream"

        try:
            descriptors.append(FileDescriptor(**data))
        except ValidationError as exc:
            logger.warning("No se pudo normalizar descriptor desde mapping: %s", exc)
        return descriptors

    if isinstance(value, (list, tuple, set)):
        for item in value:
            descriptors.extend(_normalize_to_descriptors(item))
        return descriptors

    if isinstance(value, str):
        payload, mime = _extract_base64_from_value(value)
        if payload:
            checksum = hashlib.sha1(payload.encode("utf-8")).hexdigest()
            descriptors.append(
                FileDescriptor(
                    name=f"document_{checksum[:8]}{_guess_extension(mime or 'application/pdf')}",
                    url=None,
                    size=_estimate_base64_size(payload),
                    content_type=mime or "application/pdf",
                    checksum=checksum,
                    content_base64=payload,
                )
            )
            return descriptors

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


def _unwrap_state(value: Any) -> Any:
    """Return the underlying state object when instrumentation wraps it."""
    candidate = value
    for attr in ("state", "value", "data"):
        candidate = getattr(candidate, attr, candidate)
    return candidate


class AgentUI:
    """Agent UI that classifies validation documents and manages workflow"""
    def __init__(self):
        self.human_message_prompt = HUMAN_MESSAGE_PROMPT
        self.template_sets = TEMPLATE_SETS

    @traceable
    def _state_get(
        self, state: ValidaState | Mapping[str, Any], key: str, default: Any = ""
    ) -> Any:
        candidate = _unwrap_state(state)

        if isinstance(candidate, Mapping):
            return candidate.get(key, default)

        if hasattr(candidate, "dict"):
            data = candidate.dict(exclude_none=False)
            if key in data:
                return data[key]

        return getattr(candidate, key, default)

    @traceable
    def _collect_from_state(
        self, state: ValidaState, key: str
    ) -> Iterable[FileDescriptor]:

        candidate = _unwrap_state(state)

        descriptors: list[FileDescriptor] = []

        def _coerce_name(value: Any) -> str | None:

            if value is None:

                return None

            if isinstance(value, (DocumentGroupName, DocumentName)):

                return value.value

            if hasattr(value, "value") and isinstance(getattr(value, "value"), str):

                return getattr(value, "value")

            if isinstance(value, str):

                return value

            return str(value)

        mapping = DOC_KEY_TO_GROUP.get(key)

        if mapping:

            group, document = mapping

            target_group = _coerce_name(group)

            target_document = _coerce_name(document)

            if isinstance(candidate, Mapping):

                document_groups = candidate.get("document_groups") or []

            else:

                document_groups = getattr(candidate, "document_groups", None) or []

            for entry in document_groups:

                if isinstance(entry, Mapping):

                    entry_group = entry.get("group")

                    entry_document = entry.get("document")

                    files = entry.get("files")

                else:

                    entry_group = getattr(entry, "group", None)

                    entry_document = getattr(entry, "document", None)

                    files = getattr(entry, "files", None)

                if (
                    _coerce_name(entry_group) != target_group
                    or _coerce_name(entry_document) != target_document
                ):

                    continue

                descriptors.extend(_normalize_to_descriptors(files))

        if not descriptors:

            value = self._state_get(state, key, None)

            descriptors.extend(_normalize_to_descriptors(value))

        unique: list[FileDescriptor] = []
        seen: set[tuple[str, str]] = set()

        for descriptor in descriptors:
            copy = descriptor.model_copy()
            fingerprint = _descriptor_fingerprint(copy) or f"name:{copy.name}"
            dedup_key = (fingerprint, copy.name)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            unique.append(copy)

        return unique

    @traceable
    def build_documents(
        self, state: ValidaState, set_name: str
    ) -> list[FileDescriptor]:
        cfg = self.template_sets.get(set_name, {})
        keys: list[str] = cfg.get("doc_path_list", [])
        documents: list[FileDescriptor] = []
        seen: set[tuple[str, str]] = set()

        for key in keys:
            for descriptor in self._collect_from_state(state, key):
                fingerprint = (
                    _descriptor_fingerprint(descriptor) or f"name:{descriptor.name}"
                )
                dedup_key = (fingerprint, descriptor.name)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                documents.append(descriptor)
        return documents

    @traceable
    def run(
        self, state: ValidaState, config: RunnableConfig
    ) -> Command[Literal["index_node"]]:

        return Command(
            update={
                "messages": [
                    HumanMessage(
                        content="Inicio de proceso de investigación en documentos entregados."
                    )
                ],
            },
            goto=[
                Send(
                    "index_node",
                    {
                        "set_name": set_name,
                        "documents": self.build_documents(state, set_name),
                        "data_extraction_model": self.template_sets[set_name][
                            "data_extraction_model"
                        ],
                        "tags": self.template_sets[set_name]["tags"],
                    },
                )
                for set_name in self.template_sets.keys()
            ],
        )
