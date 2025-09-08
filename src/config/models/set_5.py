from pydantic import BaseModel
from typing import List, Optional

# Set 5 - Plan de razonamiento
# - Estructura más compleja con múltiples parámetros de validación
# - activos[] con linealidad_sistema[], exactitude_del_metodo[], criterios, metrics
# - precision_sistema[] con replicas y áreas de picos
# - precision_metodo[] con porcentajes por pico
# - precision_intermedia[] con activos y analistas
# - estabilidad_sol_std[] y estabilidad_sol_mta[] con áreas en diferentes tiempos
# - estabilidad_fase_movil con replicas y tiempos
# - robustez con experimentos y parámetros

class ReplicaLinealidad(BaseModel):
    factor_respuesta: float
    concentracion: float
    area_pico: float

class LinealidadSistema(BaseModel):
    nivel: str
    replicas: List[ReplicaLinealidad]

class CriteriosLinealidad(BaseModel):
    r_min: float
    rsd_max: float
    pct_intercepto_max: float
    x_ref_100pct: float

class MetricsLinealidad(BaseModel):
    rsd_factor: float
    pendiente: float
    intercepto: float
    r: float
    r2: float
    porcentaje_intercepto: float
    cumple_global: bool

class ExactitudMetodo(BaseModel):
    nivel: str
    replicas: List[float]
    recuperacion_promedio: float
    cumple_nivel: bool

class RangoAceptacion(BaseModel):
    lo: float
    hi: float

class ActivoCompleto(BaseModel):
    nombre: str
    linealidad_sistema: List[LinealidadSistema]
    criterios: CriteriosLinealidad
    metrics: MetricsLinealidad
    exactitude_del_metodo: List[ExactitudMetodo]
    conclusion_global: str
    niveles_fuera: List[str]
    rango_aceptacion: RangoAceptacion

class PrecisionSistema(BaseModel):
    replica: int
    criterio: str
    conclusion: str
    area_pico_1: Optional[float] = None
    area_pico_2: Optional[float] = None
    area_pico_3: Optional[float] = None
    area_pico_4: Optional[float] = None
    area_pico_5: Optional[float] = None

class PrecisionMetodo(BaseModel):
    replica: int
    criterio: str
    conclusion: str
    porcentaje_pico_1: Optional[float] = None
    porcentaje_pico_2: Optional[float] = None
    porcentaje_pico_3: Optional[float] = None
    porcentaje_pico_4: Optional[float] = None
    porcentaje_pico_5: Optional[float] = None

class ActivoPrecisionIntermedia(BaseModel):
    an1: float  # analista 1 día 1
    an2: float  # analista 2 día 2

class PrecisionIntermedia(BaseModel):
    replica: int
    activos: List[ActivoPrecisionIntermedia]

class EstabilidadSolucion(BaseModel):
    nombre: str
    area_T0: float
    area_T1C1: float
    di_T1C1: float
    area_T1C2: float
    di_T1C2: float
    area_T2C1: float
    di_T2C1: float
    area_T2C2: float
    di_T2C2: float
    area_T3C1: float
    di_T3C1: float
    area_T3C2: float
    di_T3C2: float

class ReplicaFaseMovil(BaseModel):
    num: int
    t0: List[float]
    t1: List[float]
    t2: List[float]

class ExperimentoRobustez(BaseModel):
    nombre: str
    temperatura: List[float]
    flujo: List[float]
    vol_iny: List[float]
    fase_movil: List[str]

class ParamRowRobustez(BaseModel):
    parametro: str
    valores: List[float]

class Robustez(BaseModel):
    nombre: str
    param_rows: List[ParamRowRobustez]

class Set5ExtractionModel(BaseModel):
    pass

class Set5RenderingModel(BaseModel):
    # Activos con linealidad y exactitud
    activos: List[ActivoCompleto]
    
    # Precisión del sistema
    precision_sistema: List[PrecisionSistema]
    criterio_precision_sistema: str
    RSD_precision_pico_1: Optional[float] = None
    RSD_precision_pico_2: Optional[float] = None
    RSD_precision_pico_3: Optional[float] = None
    RSD_precision_pico_4: Optional[float] = None
    RSD_precision_pico_5: Optional[float] = None
    
    # Precisión del método (Repetibilidad)
    precision_metodo: List[PrecisionMetodo]
    CONC_precision_pico_1: Optional[str] = None
    CONC_precision_pico_2: Optional[str] = None
    CONC_precision_pico_3: Optional[str] = None
    CONC_precision_pico_4: Optional[str] = None
    CONC_precision_pico_5: Optional[str] = None
    criterio_rsd_max_num: float
    conclusion_global: str
    
    # Precisión intermedia
    precision_intermedia: List[PrecisionIntermedia]
    rsd_por_activo: List[float]
    criterio_txt: str
    
    # Estabilidad de soluciones
    estabilidad_sol_std: List[EstabilidadSolucion]
    concl_T1C1: str
    concl_T1C2: str
    concl_T2C1: str
    concl_T2C2: str
    concl_T3C1: str
    concl_T3C2: str
    
    estabilidad_sol_mta: List[EstabilidadSolucion]
    
    # Estabilidad de fase móvil
    headers_activos: List[str]
    replicas: List[ReplicaFaseMovil]
    rsd_t0: List[float]
    rsd_t1: List[float]
    rsd_t2: List[float]
    asim_t0: List[float]
    asim_t1: List[float]
    asim_t2: List[float]
    exact_t0: List[float]
    exact_t1: List[float]
    exact_t2: List[float]
    tr_mean_t0: List[float]
    tr_mean_t1: List[float]
    tr_mean_t2: List[float]
    resol_T0: float
    resol_T1: float
    resol_T2: float
    deltaT_T1: float
    deltaT_T2: float
    concl_T1: str
    concl_T2: str
    
    # Robustez
    experimento_robustez: List[ExperimentoRobustez]
    robustez: List[Robustez]
    conclusiones: List[str]

class Set5StructuredOutputSupervisor(BaseModel):
    # Activos con linealidad y exactitud
    activos: List[ActivoCompleto]
    
    # Precisión del sistema
    precision_sistema: List[PrecisionSistema]
    criterio_precision_sistema: str
    RSD_precision_pico_1: Optional[float] = None
    RSD_precision_pico_2: Optional[float] = None
    RSD_precision_pico_3: Optional[float] = None
    RSD_precision_pico_4: Optional[float] = None
    RSD_precision_pico_5: Optional[float] = None
    
    # Precisión del método (Repetibilidad)
    precision_metodo: List[PrecisionMetodo]
    CONC_precision_pico_1: Optional[str] = None
    CONC_precision_pico_2: Optional[str] = None
    CONC_precision_pico_3: Optional[str] = None
    CONC_precision_pico_4: Optional[str] = None
    CONC_precision_pico_5: Optional[str] = None
    criterio_rsd_max_num: float
    conclusion_global: str
    
    # Precisión intermedia
    precision_intermedia: List[PrecisionIntermedia]
    rsd_por_activo: List[float]
    criterio_txt: str
    
    # Estabilidad de soluciones
    estabilidad_sol_std: List[EstabilidadSolucion]
    concl_T1C1: str
    concl_T1C2: str
    concl_T2C1: str
    concl_T2C2: str
    concl_T3C1: str
    concl_T3C2: str
    
    estabilidad_sol_mta: List[EstabilidadSolucion]
    
    # Estabilidad de fase móvil
    headers_activos: List[str]
    replicas: List[ReplicaFaseMovil]
    rsd_t0: List[float]
    rsd_t1: List[float]
    rsd_t2: List[float]
    asim_t0: List[float]
    asim_t1: List[float]
    asim_t2: List[float]
    exact_t0: List[float]
    exact_t1: List[float]
    exact_t2: List[float]
    tr_mean_t0: List[float]
    tr_mean_t1: List[float]
    tr_mean_t2: List[float]
    resol_T0: float
    resol_T1: float
    resol_T2: float
    deltaT_T1: float
    deltaT_T2: float
    concl_T1: str
    concl_T2: str
    
    # Robustez
    experimento_robustez: List[ExperimentoRobustez]
    robustez: List[Robustez]
    conclusiones: List[str]