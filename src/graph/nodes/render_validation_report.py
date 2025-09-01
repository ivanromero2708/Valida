# -*- coding: utf-8 -*-
"""
Nodo LangGraph para renderizado de informes de validación farmacéutica.
Consolida todas las secciones de validación en un único documento DOCX.
"""

from __future__ import annotations

import re
import time
from dataclasses import asdict
from datetime import datetime
from math import sqrt, isfinite
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple, Union

from docxtpl import DocxTemplate
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from langgraph.graph import StateGraph
from pydantic import BaseModel

from src.models.validation_data import ValidationRequest, ValidationResponse


# =========================
# Configuración
# =========================
DEFAULT_TEMPLATE_PATH = Path(__file__).parent.parent.parent / "templates" / "Template_infor_val.docx"
DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent.parent.parent / "tmp_files"

# Constantes para poda de columnas
TEMPLATE_ACTIVOS_MAX_PS = 5  # Precisión del sistema
TEMPLATE_ACTIVOS_MAX_REP = 5  # Repetibilidad
TEMPLATE_ACTIVOS_MAX_PI = 5  # Precisión intermedia
MAX_ACT_FM = 5  # Fase móvil

AREA_DECIMALS = 3
RSD_DECIMALS = 2


# =========================
# Utilidades genéricas
# =========================
def fmt2(x: Optional[float]) -> str:
    """Formatea número a 2 decimales o cadena vacía si None."""
    return "" if x is None else f"{float(x):.2f}"


def safe_mean(vals: List[Optional[float]]) -> Optional[float]:
    """Calcula media segura ignorando valores None."""
    v = [float(x) for x in vals if x is not None]
    return None if not v else float(mean(v))


def robust_save(
    docx: DocxTemplate, out_path: Path, reintentos: int = 3, espera: float = 0.7
) -> Path:
    """Guarda documento DOCX con reintentos en caso de error de permisos."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    for i in range(reintentos):
        try:
            docx.save(str(out_path))
            return out_path
        except PermissionError:
            if i == reintentos - 1:
                alt = out_path.with_name(
                    out_path.stem + f"_{datetime.now():%Y%m%d_%H%M%S}_tmp.docx"
                )
                docx.save(str(alt))
                return alt
            time.sleep(espera)


def render_docxtpl(
    template_path: Path, contexto: Dict[str, Any], out_path: Path
) -> Optional[Path]:
    """Renderiza plantilla DOCX con contexto dado."""
    if not template_path.exists():
        print(f"⚠ Plantilla no encontrada: {template_path}")
        return None
    if template_path.suffix.lower() != ".docx":
        print(f"⚠ La plantilla no es .docx: {template_path}")
        return None
    
    tpl = DocxTemplate(str(template_path))
    try:
        missing = tpl.get_undeclared_template_variables(contexto)
        if missing:
            print("  · Variables no declaradas:", sorted(missing))
    except Exception:
        pass
    
    tpl.render(contexto)
    return robust_save(tpl, out_path)


# =========================
# Procesadores de secciones
# =========================

def rsd_percent(vals: List[float]) -> float:
    """Calcula RSD porcentual."""
    if len(vals) < 2:
        return 0.0
    mu = mean(vals)
    if mu == 0:
        return 0.0
    return 100.0 * (stdev(vals) / mu)


def regresion_simple(xs: List[float], ys: List[float]) -> Dict[str, float]:
    """Regresión lineal simple y = m*x + b."""
    n = len(xs)
    if n < 2:
        return {"slope": 0.0, "intercept": 0.0, "r": 0.0, "r2": 0.0}

    sx = sum(xs)
    sy = sum(ys)
    sxy = sum(x * y for x, y in zip(xs, ys))
    sx2 = sum(x * x for x in xs)
    sy2 = sum(y * y for y in ys)

    denom = n * sx2 - sx * sx
    if denom == 0:
        m = 0.0
        b = sum(ys) / n
    else:
        m = (n * sxy - sx * sy) / denom
        b = (sy - m * sx) / n

    denom_r = sqrt((n * sx2 - sx * sx) * (n * sy2 - sy * sy))
    if denom_r == 0:
        r = 0.0
    else:
        r = (n * sxy - sx * sy) / denom_r
    r2 = r * r
    if not isfinite(r):
        r, r2 = 0.0, 0.0
    return {"slope": m, "intercept": b, "r": r, "r2": r2}


class LinearityProcessor:
    """Procesador de datos de linealidad."""
    
    @staticmethod
    def process(data: Any, criterios_por_defecto: Dict[str, Any] = None) -> Dict[str, Any]:
        if criterios_por_defecto is None:
            criterios_por_defecto = {"r_min": 0.998, "rsd_max": 2.0}

        activos_out = []
        activos_in = data.activos if hasattr(data, 'activos') else data

        for a in activos_in:
            nombre = str(a.nombre if hasattr(a, 'nombre') else a["nombre"])
            
            # Normaliza réplicas
            lineas = []
            linealidad_data = a.linealidad_sistema if hasattr(a, 'linealidad_sistema') else a["linealidad_sistema"]
            for d in linealidad_data:
                nivel_data = d.dict() if hasattr(d, 'dict') else d
                lineas.append({
                    "nivel": nivel_data["nivel"],
                    "replicas": [
                        asdict(r) if hasattr(r, '__dataclass_fields__') else r
                        for r in nivel_data["replicas"]
                    ],
                })

            # Criterios
            criterios_activo = a.criterios if hasattr(a, 'criterios') else a.get("criterios", {})
            if hasattr(criterios_activo, 'dict'):
                criterios_activo = criterios_activo.dict()
            crit = {**criterios_por_defecto, **criterios_activo}

            # RSD% global de factores de respuesta
            factores_global = [
                float(rep["factor_respuesta"])
                for linea in lineas
                for rep in linea["replicas"]
            ]
            rsd_factor = rsd_percent(factores_global)

            # Regresión
            xs = [float(linea["replicas"][0]["concentracion"]) for linea in lineas]
            y_means = [
                float(mean([float(rep["area_pico"]) for rep in linea["replicas"]]))
                for linea in lineas
            ]
            reg = regresion_simple(xs, y_means)
            m, b, r, r2 = reg["slope"], reg["intercept"], reg["r"], reg["r2"]

            # %Intercepto
            x_ref = crit.get("x_ref_100pct", max(xs) if xs else 1.0)
            y_hat_ref = m * x_ref + b
            pct_intercepto = (abs(b) / y_hat_ref * 100.0) if y_hat_ref != 0 else 0.0

            # Evaluación
            cumple_r = r >= float(crit["r_min"])
            cumple_rsd = rsd_factor <= float(crit["rsd_max"])
            cumple_pct = None
            if "pct_intercepto_max" in crit:
                cumple_pct = pct_intercepto <= float(crit["pct_intercepto_max"])

            cumple_global = (
                (cumple_r and cumple_rsd)
                if (cumple_pct is None)
                else (cumple_r and cumple_rsd and bool(cumple_pct))
            )

            activos_out.append({
                "nombre": nombre,
                "linealidad_sistema": lineas,
                "criterios": crit,
                "metrics": {
                    "rsd_factor": rsd_factor,
                    "pendiente": m,
                    "intercepto": b,
                    "r": r,
                    "r2": r2,
                    "porcentaje_intercepto": pct_intercepto,
                    "cumple_global": cumple_global,
                },
            })

        return {"activos": activos_out}


class AccuracyProcessor:
    """Procesador de datos de exactitud."""
    
    @staticmethod
    def _bloque_exactitud_por_niveles(
        niveles: List[Any], rango_aceptacion: Tuple[float, float]
    ) -> List[Dict[str, Any]]:
        lo, hi = rango_aceptacion
        criterio_txt = f"El porcentaje de recuperación promedio por cada nivel debe estar entre {lo:.1f}% y {hi:.1f}%."
        salida = []
        
        for item in niveles:
            nivel_data = item.dict() if hasattr(item, 'dict') else item
            nivel = str(nivel_data["nivel"])
            reps = [float(x) for x in nivel_data["replicas"]]
            if not reps:
                raise ValueError(f"El nivel '{nivel}' no tiene réplicas.")
            prom = float(mean(reps))
            cumple = lo <= prom <= hi
            salida.append({
                "nivel": nivel,
                "replicas": [{"recuperacion": v} for v in reps],
                "recuperacion_promedio": prom,
                "criterio": criterio_txt,
                "conclusion": "Cumple" if cumple else "No cumple",
                "cumple_nivel": cumple,
            })
        return salida

    @staticmethod
    def process(data: Any, rango_aceptacion_por_defecto: Tuple[float, float] = (98.0, 102.0)) -> Dict[str, Any]:
        lista = []
        activos = data.activos if hasattr(data, 'activos') else data
        
        for a in activos:
            activo_data = a.dict() if hasattr(a, 'dict') else a
            nombre = str(activo_data["nombre"])
            niveles = activo_data["niveles"]
            rango = tuple(activo_data.get("rango_aceptacion", rango_aceptacion_por_defecto))
            
            exacts = AccuracyProcessor._bloque_exactitud_por_niveles(niveles, rango)
            fuera = [e for e in exacts if not e["cumple_nivel"]]
            conclusion_global = "Cumple" if not fuera else "No cumple"
            
            lista.append({
                "nombre": nombre,
                "exactitude_del_metodo": exacts,
                "conclusion_global": conclusion_global,
                "niveles_fuera": [e["nivel"] for e in fuera],
                "rango_aceptacion": {"lo": rango[0], "hi": rango[1]},
            })
        
        return {
            "activos": lista,
            "activos_titulo": ", ".join([a["nombre"] for a in lista]) if lista else "",
            "fecha_render": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }


class MaterialsProcessor:
    """Procesador de datos de materiales."""
    
    @staticmethod
    def process(data: Any) -> Dict[str, Any]:
        if hasattr(data, 'dict'):
            return data.dict()
        return data


class SystemPrecisionProcessor:
    """Procesador de precisión del sistema."""
    
    @staticmethod
    def _pad_to_max(lst: List[Any], size: int, fill: Any) -> List[Any]:
        out = list(lst)
        if len(out) < size:
            out += [fill] * (size - len(out))
        return out[:size]

    @staticmethod
    def process(data: Any) -> Dict[str, Any]:
        base = data.dict() if hasattr(data, 'dict') else data
        activos_in = base.get("activos", [])
        if not activos_in:
            raise ValueError("Faltan activos en base['activos'].")

        umbral_global = float(base.get("umbral_rsd", 2.0))
        umbrales_por_activo = base.get("umbrales_rsd_por_activo", None)
        if umbrales_por_activo is not None:
            umbrales_por_activo = list(map(float, umbrales_por_activo))
            if len(umbrales_por_activo) < len(activos_in):
                umbrales_por_activo += [umbral_global] * (
                    len(activos_in) - len(umbrales_por_activo)
                )

        activos_proc, max_reps = [], 0
        for a in activos_in:
            activo_data = a.dict() if hasattr(a, 'dict') else a
            areas = list(map(float, activo_data.get("areas", [])))
            rsd = round(rsd_percent(areas), RSD_DECIMALS)
            activos_proc.append({"areas": areas, "rsd": rsd})
            max_reps = max(max_reps, len(areas))

        if max_reps == 0:
            raise ValueError("No hay réplicas para calcular precisión del sistema.")

        cumple_por_activo = []
        for idx, ap in enumerate(activos_proc):
            umbral_i = (
                umbrales_por_activo[idx]
                if umbrales_por_activo is not None
                else umbral_global
            )
            cumple_por_activo.append(ap["rsd"] <= round(float(umbral_i), RSD_DECIMALS))
        conclusion_global = "Cumple" if all(cumple_por_activo) else "No cumple"

        criterio_in = base.get("criterio", "").strip()
        criterio = (
            criterio_in
            if criterio_in
            else f"El %RSD de {max_reps} inyecciones replicadas de la solución estándar es ≤ {umbral_global:.1f}%."
        )

        activos_proc = SystemPrecisionProcessor._pad_to_max(
            activos_proc, TEMPLATE_ACTIVOS_MAX_PS, {"areas": [], "rsd": ""}
        )

        rows = []
        for i in range(max_reps):
            row = {"replica": i + 1, "criterio": criterio, "conclusion": conclusion_global}
            for j in range(TEMPLATE_ACTIVOS_MAX_PS):
                val = (
                    activos_proc[j]["areas"][i] if i < len(activos_proc[j]["areas"]) else ""
                )
                row[f"area_pico_{j+1}"] = "" if val == "" else f"{val:.{AREA_DECIMALS}f}"
            rows.append(row)

        rsd_vals = [ap["rsd"] for ap in activos_proc]
        rsd_vals = SystemPrecisionProcessor._pad_to_max(rsd_vals, TEMPLATE_ACTIVOS_MAX_PS, "")
        rsd_ctx = {
            f"RSD_precision_pico_{i+1}": (
                "" if rsd_vals[i] == "" else f"{rsd_vals[i]:.{RSD_DECIMALS}f}"
            )
            for i in range(TEMPLATE_ACTIVOS_MAX_PS)
        }
        
        return {
            "precision_sistema": rows,
            "conclusion_global_precision_sistema": conclusion_global,
            "criterio_precision_sistema": criterio,
            **rsd_ctx,
        }


# =========================
# Nodo principal
# =========================

class ValidationState(BaseModel):
    """Estado del grafo de validación."""
    validation_request: ValidationRequest
    processed_sections: List[str] = []
    context_data: Dict[str, Any] = {}
    errors: List[str] = []
    warnings: List[str] = []
    output_file: Optional[str] = None


def render_validation_report_node(state: ValidationState) -> ValidationState:
    """
    Nodo principal para renderizar informe de validación.
    Consolida todas las secciones en un único documento DOCX.
    """
    start_time = time.time()
    request = state.validation_request
    context = {"project_info": request.project_info.dict()}
    processed_sections = []
    errors = []
    warnings = []

    try:
        # Procesar cada sección si está presente
        if request.linearity_data:
            try:
                linearity_context = LinearityProcessor.process(
                    request.linearity_data,
                    request.linearity_data.criterios_por_defecto
                )
                context.update(linearity_context)
                processed_sections.append("linearity")
            except Exception as e:
                errors.append(f"Error procesando linealidad: {str(e)}")

        if request.accuracy_data:
            try:
                accuracy_context = AccuracyProcessor.process(
                    request.accuracy_data,
                    request.accuracy_data.rango_aceptacion_por_defecto
                )
                context.update(accuracy_context)
                processed_sections.append("accuracy")
            except Exception as e:
                errors.append(f"Error procesando exactitud: {str(e)}")

        if request.materials_data:
            try:
                materials_context = MaterialsProcessor.process(request.materials_data)
                context.update(materials_context)
                processed_sections.append("materials")
            except Exception as e:
                errors.append(f"Error procesando materiales: {str(e)}")

        if request.system_precision_data:
            try:
                precision_context = SystemPrecisionProcessor.process(request.system_precision_data)
                context.update(precision_context)
                processed_sections.append("system_precision")
            except Exception as e:
                errors.append(f"Error procesando precisión del sistema: {str(e)}")

        # Determinar rutas
        template_path = Path(request.template_path) if request.template_path else DEFAULT_TEMPLATE_PATH
        if request.output_path:
            output_path = Path(request.output_path)
        else:
            output_path = DEFAULT_OUTPUT_PATH / f"validation_report_{datetime.now():%Y%m%d_%H%M%S}.docx"

        # Renderizar documento
        if not errors:  # Solo renderizar si no hay errores críticos
            try:
                result_path = render_docxtpl(template_path, context, output_path)
                if result_path:
                    state.output_file = str(result_path)
                    print(f"✔ Informe de validación generado: {result_path}")
                else:
                    errors.append("Error al generar el documento DOCX")
            except Exception as e:
                errors.append(f"Error al renderizar documento: {str(e)}")

    except Exception as e:
        errors.append(f"Error general en procesamiento: {str(e)}")

    # Actualizar estado
    state.processed_sections = processed_sections
    state.context_data = context
    state.errors = errors
    state.warnings = warnings

    processing_time = time.time() - start_time
    print(f"Procesamiento completado en {processing_time:.2f} segundos")
    print(f"Secciones procesadas: {', '.join(processed_sections)}")
    if errors:
        print(f"Errores: {len(errors)}")
    if warnings:
        print(f"Advertencias: {len(warnings)}")

    return state


def build_validation_graph() -> StateGraph:
    """Construye el grafo de validación."""
    graph = StateGraph(ValidationState)
    
    # Agregar nodo de renderizado
    graph.add_node("render_report", render_validation_report_node)
    
    # Definir punto de entrada
    graph.set_entry_point("render_report")
    
    # Compilar grafo
    return graph.compile()


# =========================
# Función de conveniencia
# =========================

def generate_validation_report(
    validation_request: ValidationRequest
) -> ValidationResponse:
    """
    Función de conveniencia para generar informe de validación.
    
    Args:
        validation_request: Solicitud de validación con todos los datos
        
    Returns:
        ValidationResponse: Respuesta con resultado de la operación
    """
    start_time = time.time()
    
    try:
        # Crear grafo y ejecutar
        graph = build_validation_graph()
        initial_state = ValidationState(validation_request=validation_request)
        
        result = graph.invoke(initial_state)
        
        processing_time = time.time() - start_time
        
        return ValidationResponse(
            success=len(result.errors) == 0,
            output_file=result.output_file,
            sections_processed=result.processed_sections,
            errors=result.errors,
            warnings=result.warnings,
            processing_time=processing_time,
            metadata={
                "template_used": validation_request.template_path or str(DEFAULT_TEMPLATE_PATH),
                "sections_requested": [
                    section for section in [
                        "linearity" if validation_request.linearity_data else None,
                        "accuracy" if validation_request.accuracy_data else None,
                        "materials" if validation_request.materials_data else None,
                        "system_precision" if validation_request.system_precision_data else None,
                        "repeatability" if validation_request.repeatability_data else None,
                        "intermediate_precision" if validation_request.intermediate_precision_data else None,
                        "stability" if validation_request.stability_data else None,
                        "mobile_phase" if validation_request.mobile_phase_data else None,
                        "robustness" if validation_request.robustness_data else None,
                    ] if section
                ]
            }
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        return ValidationResponse(
            success=False,
            errors=[f"Error crítico: {str(e)}"],
            processing_time=processing_time
        )