from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Protocolo de validación
class CriterioValidacion(BaseModel):
    parametro: Literal[
        "Linealidad", "Exactitud del método (Recuperación)", "Precisión del sistema",
        "Precisión del método (´Repetibilidad)", "Precisión intermedia",
        "Precisión del método (Reproducibilidad)", "Rango (Intervalo)",
        "Robustez del método", "Estabilidad analítica de las soluciones",
        "Estabilidad analítica de la fase móvil"
    ] = Field(..., description="Nombre del parametro de validación")
    criterio_aceptacion: str = Field(..., description="Descripción de texto del criterio de aceptación del parámetro en el protocolo de validación")

# Variables auxiliares
class DataInyeccion(BaseModel):
    No: int = Field(..., description="Número consecutivo que identifica el pico en la data cromatográfica recuperada de la inyección.")
    peak_name: str = Field(..., description="Nombre del pico en la data cromatográfica recuperada de la inyección. Usualmente corresponde al analito de estudio")
    analito: str = Field(..., description="Nombre del analito asociado al pico. Usualmente corresponde al nombre del pico")
    retention_time: float = Field(..., description="NÚMERO EXACTO CON TODOS LOS DECIMALES DEL Tiempo de retención del pico en la data cromatográfica recuperada de la inyección.")
    area: float = Field(..., description="NÚMERO EXACTO CON TODOS LOS DECIMALES DEL Área bajo la curva del pico en la data cromatográfica recuperada de la inyección. Insisto, este número tiene decimales.. debes extraerlos en formato XXXXX.XXXXX")
    # ⬇️ Opcionales de verdad
    cal_amount: Optional[float] = Field(None, description="Cantidad calificada del pico en la data cromatográfica recuperada de la inyección.")
    resolution: Optional[float] = Field(None, description="Resolución entre los picos de los ingredientes activos en la data cromatográfica recuperada de la inyección.")
    t_plates_usp: Optional[float] = Field(None, description="T-plates USP del pico en la data cromatográfica recuperada de la inyección.")
    assymetry: Optional[float] = Field(None, description="Asimetría del pico en la data cromatográfica recuperada de la inyección.")
    amount: Optional[float] = Field(None, description="Cantidad del pico en la data cromatográfica recuperada de la inyección. Usualmente se acompaña de unidades tales como mg/mL, entre otras")

class DataChromaEstFM(BaseModel):
    nombre_muestra: str = Field(..., description="Nombre de la muestra que se analiza en la inyeccion. Puede empezar con 'SST', 'Fase Movil', 'Solucion Estandar', entre otros")
    referencia_analitica: str = Field(..., description = "Referencia analitica de la muestra. Usualmente empieza como HT")
    dilution_factor: float = Field(..., description="Factor de dilución de la muestra. Usualmente es un número que aparece al lado del strin 'Dilution Factor', o similar")
    weight: float = Field(..., description="Peso de la muestra. Usualmente es un número que aparece al lado del strin 'Weight', o similar")
    no_inyeccion: int = Field(..., description="Número de la inyección que aparece al lado de un string similar a 'Injection Number', o similar")
    # ⬇️ Opcional de verdad
    data_inyecciones: Optional[List[DataInyeccion]] = Field(
        None, description= "Lista de diccionarios que contiene los picos obtenidos en la data cromatográfica de la inyección"
    )

# Box Extraction
class Set10BoxDetector(BaseModel):
    """Detector para bboxes que parezcan tablas de cromatografía útiles para Set10."""
    is_set10_candidate: bool = Field(..., description="True si la imagen contiene una tabla de cromatografía relevante para Set10")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza del clasificador")
    hints_columns_presentes: List[str] = Field(
        default_factory=list,
        description="Columnas detectadas: e.g., 'No', 'Peak', 'Retention time', 'Area', 'USP Tailing', 'Resolution', 'Amount', etc."
    )
    possible_section: Optional[Literal["Fase Movil","SST","Estandar","Muestra","Desconocido"]] = Field(
        None, description="Heurística de sección"
    )
    notes: Optional[str] = Field(None, description="Notas breves (opcional)")

class ExtraccionDaExtraccionArchivoDataTiempo(BaseModel):
    page_index: Optional[int] = Field(None, description="Página de origen")
    bbox_id: Optional[str] = Field(None, description="ID del bbox en la página")
    # ⬇️ Hacerlo opcional: el pipeline lo inyecta si falta
    nombre_archivo: Optional[str] = Field(
        None, description= "Nombre del archivo de donde se hará la extracción de datos.. Se puede inferir el tiempo de allí, por eso es importante que lo extraigas"
    )
    data_estabilidad_fase_movil: List[DataChromaEstFM] = Field(
        ..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la fase movil."
    )
    criterios_validacion: Optional[List[CriterioValidacion]] = Field(
        None, description="Lista de criterios de aceptación de las pruebas de validación presentes en el protocolo de validación"
    )

# Extracción de datos (agregable aguas arriba si quieres consolidar varias tablas)
class Set10ExtractionModel(BaseModel):
    """Modelo de validación de datos para Salida estructurada Estabilidad de la fase movil"""
    data_bruta_estabilidad_fase_movil: List[ExtraccionDaExtraccionArchivoDataTiempo] = Field(
        ..., description="Listado de diccionarios que contiene toda la información relacionada con la validación de la fase movil."
    )

# Salida Estructurada
class ReplicaData(BaseModel):
    replica: int = Field(..., description="Número de la réplica (e.g., 1, 2, 3).")
    areas_system: float = Field(..., description="Valor del área del sistema para esta réplica.")
    tiempo_retencion: float = Field(..., description="Valor del tiempo de retención para esta réplica.")
    usp_tailing: float = Field(..., description="Valor de USP Tailing para esta réplica.")

class ResultadosPorTiempo(BaseModel):
    tiempo_label: str = Field(..., description="Etiqueta del punto de tiempo, ej: 'Tiempo 0 (Día 0)' o 'Tiempo 1 (Día 6)'.")
    replicas_data: List[ReplicaData] = Field(..., description="Lista de datos para cada una de las réplicas.")
    promedio_areas_system: Optional[float] = Field(None, description="Promedio calculado de las áreas del sistema.")
    promedio_tiempo_retencion: Optional[float] = Field(None, description="Promedio calculado de los tiempos de retención.")
    promedio_usp_tailing: Optional[float] = Field(None, description="Promedio calculado de los valores de USP Tailing.")
    rsd_areas_system: Optional[float] = Field(None, description="RSD (%) calculado para las áreas del sistema.")
    conclusion_rsd_areas: str = Field("Pendiente", description="Conclusión de si el RSD de las áreas cumple el criterio.")
    conclusion_tiempo_retencion: str = Field("Pendiente", description="Conclusión de si el tiempo de retención cumple el criterio.")
    conclusion_usp_tailing: str = Field("Pendiente", description="Conclusión de si el USP Tailing cumple el criterio.")

class CriterioAceptacion(BaseModel):
    parametro: str = Field(..., description="Parámetro evaluado, ej: 'RSD de áreas', 'Variación Tiempo de Retención', 'USP Tailing', 'Resolución'.")
    criterio: str = Field(..., description="Descripción literal del criterio de aceptación, ej: 'debe ser menor o igual a 2.0%'.")

class AnalitoResultados(BaseModel):
    nombre_analito: str = Field(..., description="Nombre del analito evaluado, ej: 'Acetaminofen'.")
    resultados_por_tiempo: List[ResultadosPorTiempo] = Field(..., description="Lista de resultados para cada punto de tiempo evaluado.")
    criterios_aceptacion: List[CriterioAceptacion] = Field(..., description="Lista de los criterios de aceptación aplicables.")
    conclusion_general_analito: str = Field("Pendiente", description="Conclusión general sobre si el analito cumple con todos los criterios en todos los tiempos.")

class Set10StructuredOutputSupervisor(BaseModel):
    titulo_parametro: str = Field(..., description="Título del parámetro de validación, ej: 'Resultados Estabilidad de la Fase Móvil'.")
    analitos_estabilidad_fasemovil: List[AnalitoResultados] = Field(..., description="Lista de resultados para cada analito encontrado.")
    referencia_analitica_estabilidad_fasemovil: Optional[str] = Field(None, description="Código de referencia del reporte o análisis, si está disponible (ej. HT...).")
