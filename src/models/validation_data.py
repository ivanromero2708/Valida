# -*- coding: utf-8 -*-
"""
Modelos de datos para validación farmacéutica.
Basado en las estructuras definidas en tests/final.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, validator


# =========================
# Modelos Base
# =========================

@dataclass
class Replica:
    """Réplica individual para análisis de linealidad."""
    concentracion: float  # mg/mL
    area_pico: float
    factor_respuesta: float  # típicamente area/concentración


class ProjectInfo(BaseModel):
    """Información general del proyecto de validación."""
    title: str = Field(..., description="Título del informe de validación")
    product: str = Field(..., description="Nombre del producto farmacéutico")
    analyst: str = Field(..., description="Analista responsable")
    method: Optional[str] = Field(None, description="Método analítico utilizado")
    date: Optional[datetime] = Field(default_factory=datetime.now, description="Fecha de análisis")
    laboratory: Optional[str] = Field(None, description="Laboratorio")
    equipment: Optional[str] = Field(None, description="Equipo utilizado")


# =========================
# Sección 1: Linealidad
# =========================

class LinearityLevel(BaseModel):
    """Nivel de concentración para linealidad."""
    nivel: int = Field(..., description="Número del nivel")
    replicas: List[Dict[str, float]] = Field(..., description="Réplicas del nivel")


class LinearityData(BaseModel):
    """Datos de linealidad del sistema para un activo."""
    nombre: str = Field(..., description="Nombre del activo")
    linealidad_sistema: List[LinearityLevel] = Field(..., description="Niveles de linealidad")
    criterios: Optional[Dict[str, float]] = Field(
        default={
            "r_min": 0.998,
            "rsd_max": 2.0,
            "pct_intercepto_max": 2.0,
            "x_ref_100pct": 0.3000
        },
        description="Criterios de aceptación"
    )


class LinearityRequest(BaseModel):
    """Solicitud completa de análisis de linealidad."""
    activos: List[LinearityData] = Field(..., description="Lista de activos a analizar")
    criterios_por_defecto: Optional[Dict[str, float]] = Field(
        default={"r_min": 0.998, "rsd_max": 2.0},
        description="Criterios por defecto"
    )


# =========================
# Sección 2: Exactitud
# =========================

class AccuracyLevel(BaseModel):
    """Nivel de exactitud con réplicas."""
    nivel: str = Field(..., description="Nivel (ej: '80%', '100%', '120%')")
    replicas: List[float] = Field(..., description="Porcentajes de recuperación")


class AccuracyData(BaseModel):
    """Datos de exactitud para un activo."""
    nombre: str = Field(..., description="Nombre del activo")
    niveles: List[AccuracyLevel] = Field(..., description="Niveles de exactitud")
    rango_aceptacion: Optional[Tuple[float, float]] = Field(
        default=(98.0, 102.0),
        description="Rango de aceptación (min, max)"
    )


class AccuracyRequest(BaseModel):
    """Solicitud completa de análisis de exactitud."""
    activos: List[AccuracyData] = Field(..., description="Lista de activos")
    rango_aceptacion_por_defecto: Tuple[float, float] = Field(
        default=(98.0, 102.0),
        description="Rango por defecto"
    )


# =========================
# Sección 3: Materiales
# =========================

class SampleInfo(BaseModel):
    """Información de muestra utilizada."""
    nombre: str = Field(..., description="Nombre de la muestra")
    codigo: str = Field(..., description="Código de la muestra")
    lote: str = Field(..., description="Lote")
    codigo_interno_cim: str = Field(..., description="Código interno CIM")


class StandardInfo(BaseModel):
    """Información de estándar de referencia."""
    nombre: str = Field(..., description="Nombre del estándar")
    fabricante: str = Field(..., description="Fabricante")
    lote: str = Field(..., description="Lote")
    numero_parte: str = Field(..., description="Número de parte")
    codigo_identificacion: str = Field(..., description="Código de identificación")
    concentracion: str = Field(..., description="Concentración")
    vencimiento: str = Field(..., description="Fecha de vencimiento")


class ReagentInfo(BaseModel):
    """Información de reactivo."""
    nombre: str = Field(..., description="Nombre del reactivo")
    fabricante: str = Field(..., description="Fabricante")
    lote: str = Field(..., description="Lote")
    numero_parte: str = Field(..., description="Número de parte")
    vencimiento: str = Field(..., description="Fecha de vencimiento")


class MaterialInfo(BaseModel):
    """Información de material."""
    nombre: str = Field(..., description="Nombre del material")
    fabricante: str = Field(..., description="Fabricante")
    numero_parte: str = Field(..., description="Número de parte")
    lote: str = Field(..., description="Lote")


class EquipmentInfo(BaseModel):
    """Información de equipo."""
    nombre: str = Field(..., description="Nombre del equipo")
    consecutivo: str = Field(..., description="Consecutivo")
    fabricante: str = Field(..., description="Fabricante")
    modelo: str = Field(..., description="Modelo")
    serial: str = Field(..., description="Número de serie")
    prox_actividad: str = Field(..., description="Próxima actividad de mantenimiento")


class ColumnInfo(BaseModel):
    """Información de columna cromatográfica."""
    descripcion: str = Field(..., description="Descripción de la columna")
    fabricante: str = Field(..., description="Fabricante")
    numero_parte: str = Field(..., description="Número de parte")
    serial: str = Field(..., description="Número de serie")
    numero_interno: str = Field(..., description="Número interno")


class MaterialsData(BaseModel):
    """Datos completos de materiales e insumos."""
    muestra_utilizadas: List[SampleInfo] = Field(default_factory=list)
    estandar_utilizados: List[StandardInfo] = Field(default_factory=list)
    reactivo_utilizados: List[ReagentInfo] = Field(default_factory=list)
    materiales_utilizados: List[MaterialInfo] = Field(default_factory=list)
    equipos_utilizados: List[EquipmentInfo] = Field(default_factory=list)
    columna_utilizada: List[ColumnInfo] = Field(default_factory=list)


# =========================
# Sección 4: Precisión del Sistema
# =========================

class SystemPrecisionData(BaseModel):
    """Datos de precisión del sistema para un activo."""
    nombre: str = Field(..., description="Nombre del activo")
    areas: List[float] = Field(..., description="Áreas de pico")


class SystemPrecisionRequest(BaseModel):
    """Solicitud de análisis de precisión del sistema."""
    activos: List[SystemPrecisionData] = Field(..., description="Lista de activos")
    umbral_rsd: float = Field(default=2.0, description="Umbral RSD global")
    umbrales_rsd_por_activo: Optional[List[float]] = Field(
        None, description="Umbrales específicos por activo"
    )
    criterio: Optional[str] = Field(None, description="Criterio personalizado")


# =========================
# Sección 5: Repetibilidad
# =========================

class RepeatabilityData(BaseModel):
    """Datos de repetibilidad para un activo."""
    nombre: str = Field(..., description="Nombre del activo")
    porcentajes: List[float] = Field(..., description="Porcentajes obtenidos")
    rsd: Optional[float] = Field(None, description="RSD calculado (opcional)")


class RepeatabilityRequest(BaseModel):
    """Solicitud de análisis de repetibilidad."""
    criterio: str = Field(..., description="Criterio de aceptación")
    criterio_rsd_max: Optional[float] = Field(None, description="RSD máximo permitido")
    conclusion: Optional[str] = Field(None, description="Conclusión manual")
    activos: List[RepeatabilityData] = Field(..., description="Lista de activos")


# =========================
# Sección 6: Precisión Intermedia
# =========================

class IntermediatePrecisionReplica(BaseModel):
    """Réplica de precisión intermedia."""
    replica: int = Field(..., description="Número de réplica")
    activos: List[Optional[Dict[str, Optional[float]]]] = Field(
        ..., description="Datos por activo (an1, an2)"
    )


class IntermediatePrecisionRequest(BaseModel):
    """Solicitud de análisis de precisión intermedia."""
    filas_input: List[IntermediatePrecisionReplica] = Field(..., description="Datos de entrada")
    criterio_max: float = Field(default=2.0, description="Criterio máximo RSD")


# =========================
# Sección 7: Estabilidad de Soluciones
# =========================

class StabilityMeasurement(BaseModel):
    """Medición de estabilidad por tiempo y condición."""
    T0: Optional[Union[float, List[float]]] = Field(None, description="Tiempo inicial")
    T1: Optional[Dict[str, Union[float, List[float]]]] = Field(None, description="Tiempo 1")
    T2: Optional[Dict[str, Union[float, List[float]]]] = Field(None, description="Tiempo 2")
    T3: Optional[Dict[str, Union[float, List[float]]]] = Field(None, description="Tiempo 3")


class StabilityData(BaseModel):
    """Datos de estabilidad para un activo."""
    nombre: str = Field(..., description="Nombre del activo")
    medidas: StabilityMeasurement = Field(..., description="Mediciones por tiempo")


class StabilityRequest(BaseModel):
    """Solicitud de análisis de estabilidad."""
    activos_input: List[StabilityData] = Field(..., description="Lista de activos")
    tiempos: List[str] = Field(default=["T0", "T1", "T2", "T3"], description="Tiempos de medición")
    condiciones_por_tiempo: Dict[str, List[str]] = Field(
        default={"T1": ["C1", "C2"], "T2": ["C1", "C2"], "T3": ["C1", "C2"]},
        description="Condiciones por tiempo"
    )
    criterio_delta_max_pct: float = Field(default=2.0, description="Delta máximo permitido (%)")
    criterio_sim_lo: float = Field(default=98.0, description="Límite inferior similitud (%)")
    criterio_sim_hi: float = Field(default=102.0, description="Límite superior similitud (%)")


# =========================
# Sección 8: Estabilidad de Fase Móvil
# =========================

class MobilePhaseReplica(BaseModel):
    """Réplica de fase móvil."""
    num: int = Field(..., description="Número de réplica")
    t0: List[float] = Field(..., description="Tiempos T0")
    t1: List[float] = Field(..., description="Tiempos T1")
    t2: List[float] = Field(..., description="Tiempos T2")


class MobilePhaseRequest(BaseModel):
    """Solicitud de análisis de estabilidad de fase móvil."""
    nombres_activos: List[str] = Field(..., description="Nombres de activos")
    replicas_input: List[MobilePhaseReplica] = Field(..., description="Réplicas")
    rsd_t0: Optional[List[Optional[float]]] = Field(None, description="RSD T0")
    rsd_t1: Optional[List[Optional[float]]] = Field(None, description="RSD T1")
    rsd_t2: Optional[List[Optional[float]]] = Field(None, description="RSD T2")
    asim_t0: Optional[List[Optional[float]]] = Field(None, description="Asimetría T0")
    asim_t1: Optional[List[Optional[float]]] = Field(None, description="Asimetría T1")
    asim_t2: Optional[List[Optional[float]]] = Field(None, description="Asimetría T2")
    exact_t0: Optional[List[Optional[float]]] = Field(None, description="Exactitud T0")
    exact_t1: Optional[List[Optional[float]]] = Field(None, description="Exactitud T1")
    exact_t2: Optional[List[Optional[float]]] = Field(None, description="Exactitud T2")
    resol_T0: Optional[float] = Field(None, description="Resolución T0")
    resol_T1: Optional[float] = Field(None, description="Resolución T1")
    resol_T2: Optional[float] = Field(None, description="Resolución T2")
    concl_T1: str = Field(default="Cumple", description="Conclusión T1")
    concl_T2: str = Field(default="Cumple", description="Conclusión T2")
    criterio_txt: str = Field(
        default="La fase móvil se considera estable si el rango de variación del tiempo de retención es ±3 minutos respecto al análisis inicial, no hay picos fantasmas/división, cada tiempo cumple adecuabilidad del sistema (RSD ≤ 2.0%, asimetría ≤ 1.6, resolución ≥ 5.0) y el factor de exactitud se mantiene en 98.0–102.0%.",
        description="Criterio de evaluación"
    )


# =========================
# Sección 9: Robustez
# =========================

class RobustnessParameter(BaseModel):
    """Parámetro de robustez."""
    parametro: str = Field(..., description="Nombre del parámetro")
    valores: List[str] = Field(..., description="Valores obtenidos")


class RobustnessCompound(BaseModel):
    """Compuesto para análisis de robustez."""
    nombre: str = Field(..., description="Nombre del compuesto")
    param_rows: List[RobustnessParameter] = Field(..., description="Parámetros evaluados")


class RobustnessRequest(BaseModel):
    """Solicitud de análisis de robustez."""
    compuestos: List[RobustnessCompound] = Field(..., description="Lista de compuestos")
    criterio_txt: str = Field(
        default="Las especificaciones del Test de Adecuabilidad del Sistema (SST) deben cumplirse en todas las condiciones analizadas. El porcentaje de cambio |di| obtenido en cada condición evaluada debe ser ≤ 2.0% respecto a la condición nominal.",
        description="Criterio de evaluación"
    )
    conclusiones: List[str] = Field(..., description="Conclusiones por condición")


# =========================
# Modelo Principal
# =========================

class ValidationRequest(BaseModel):
    """Solicitud completa de validación."""
    project_info: ProjectInfo = Field(..., description="Información del proyecto")
    
    # Secciones opcionales
    linearity_data: Optional[LinearityRequest] = Field(None, description="Datos de linealidad")
    accuracy_data: Optional[AccuracyRequest] = Field(None, description="Datos de exactitud")
    materials_data: Optional[MaterialsData] = Field(None, description="Datos de materiales")
    system_precision_data: Optional[SystemPrecisionRequest] = Field(None, description="Precisión del sistema")
    repeatability_data: Optional[RepeatabilityRequest] = Field(None, description="Repetibilidad")
    intermediate_precision_data: Optional[IntermediatePrecisionRequest] = Field(None, description="Precisión intermedia")
    stability_data: Optional[StabilityRequest] = Field(None, description="Estabilidad de soluciones")
    mobile_phase_data: Optional[MobilePhaseRequest] = Field(None, description="Estabilidad de fase móvil")
    robustness_data: Optional[RobustnessRequest] = Field(None, description="Robustez")
    
    # Configuración de salida
    output_path: Optional[str] = Field(None, description="Ruta de archivo de salida")
    template_path: Optional[str] = Field(None, description="Ruta de plantilla personalizada")
    
    @validator('output_path')
    def validate_output_path(cls, v):
        if v and not v.endswith('.docx'):
            return f"{v}.docx"
        return v


class ValidationResponse(BaseModel):
    """Respuesta de validación."""
    success: bool = Field(..., description="Éxito de la operación")
    output_file: Optional[str] = Field(None, description="Archivo generado")
    sections_processed: List[str] = Field(default_factory=list, description="Secciones procesadas")
    errors: List[str] = Field(default_factory=list, description="Errores encontrados")
    warnings: List[str] = Field(default_factory=list, description="Advertencias")
    processing_time: Optional[float] = Field(None, description="Tiempo de procesamiento (segundos)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
