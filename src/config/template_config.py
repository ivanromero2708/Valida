from src.config.models.set_2 import (Set2ExtractionModel,Set2StructuredOutputSupervisor,)
from src.config.models.set_3 import (Set3ExtractionModel,Set3StructuredOutputSupervisor,)        
from src.config.models.set_4 import (Set4ExtractionModel,Set4StructuredOutputSupervisor,)
from src.config.models.set_5 import (Set5ExtractionModel,Set5StructuredOutputSupervisor,)
from src.config.models.set_6 import (Set6ExtractionModel,Set6StructuredOutputSupervisor,)
from src.config.models.set_7 import (Set7ExtractionModel,Set7StructuredOutputSupervisor,)
from src.config.models.set_8 import (Set8ExtractionModel,Set8StructuredOutputSupervisor,)
from src.config.models.set_10 import (Set10ExtractionModel,Set10StructuredOutputSupervisor,)
from src.config.models.set_11 import (Set11ExtractionModel,Set11StructuredOutputSupervisor,)
from src.config.models.protocolo import ParametrosValidacion

from src.config.prompt_sets import (RULES_SET_2,RULES_SET_3,RULES_SET_4,RULES_SET_5,RULES_SET_6,RULES_SET_7,RULES_SET_8,RULES_SET_10,RULES_SET_11)


TEMPLATE_SETS_TRIAL = {
    "Protocolo": {
        "human_message_prompt": "",
        "doc_path_list": [
            "dir_protocolo",
        ],
        "data_extraction_model": ParametrosValidacion,
        "tags": ["criterios_validacion"],
    },
    "Set 2": {
        "human_message_prompt": RULES_SET_2,
        "doc_path_list": [
            "dir_protocolo",
            "dir_hoja_trabajo_preparacion",
            "dirs_bitacora_preparacion",
            "dirs_hoja_trabajo_linealidad",
            "dirs_bitacoras_linealidad",
            "dirs_soportes_cromatográficos_linealidad",
            "dirs_hoja_trabajo_precision_sistema",
            "dirs_bitacoras_precision_sistema",
            "dirs_soportes_cromatográficos_precision_sistema",
            "dirs_hoja_trabajo_precision_metodo",
            "dirs_bitacoras_precision_metodo",
            "dirs_soportes_cromatográficos_precision_metodo",
            "dirs_hoja_trabajo_precision_intermedia",
            "dirs_bitacoras_precision_intermedia",
            "dirs_soportes_cromatográficos_precision_intermedia",
            "dirs_hoja_trabajo_exactitud",
            "dirs_bitacoras_exactitud",
            "dirs_soportes_cromatográficos_exactitud",
            "dirs_hoja_trabajo_estabilidad_solucion_estandar",
            "dirs_bitacoras_estabilidad_solucion_estandar",
            "dirs_soportes_cromatográficos_estabilidad_solucion_estandar",
            "dirs_hoja_trabajo_estabilidad_solucion_muestra",
            "dirs_bitacoras_estabilidad_solucion_muestra",
            "dirs_soportes_cromatográficos_estabilidad_solucion_muestra",
            "dirs_hoja_trabajo_estabilidad_solucion_fase_movil",
            "dirs_bitacoras_estabilidad_solucion_fase_movil",
            "dirs_soportes_cromatográficos_estabilidad_solucion_fase_movil",
            "dirs_hoja_trabajo_robustez",
            "dirs_bitacoras_robustez",
            "dirs_soportes_cromatográficos_robustez",
        ],
        "data_extraction_model": Set2ExtractionModel,
        "structured_output_supervisor": Set2StructuredOutputSupervisor,
        "tags": [
            "muestra_utilizadas",
            "estandar_utilizados",
            "reactivo_utilizados",
            "materiales_utilizados",
            "equipos_utilizados",
            "columna_utilizada",
        ],
    },
    "Set 3": {
        "human_message_prompt": RULES_SET_3,
        "doc_path_list": [
            #"dir_protocolo",
            "dir_reporte_lims_linealidad",
            "dirs_hoja_trabajo_linealidad",
            "dirs_bitacoras_linealidad",
            "dirs_soportes_cromatográficos_linealidad",
        ],
        "data_extraction_model": Set3ExtractionModel,
        "structured_output_supervisor": Set3StructuredOutputSupervisor,
        "tags": ["activos_linealidad", "referencia_linealidad"],
    },
    "Set 4": {
        "human_message_prompt": RULES_SET_4,
        "doc_path_list": [
            #"dir_protocolo",
            "dir_reporte_lims_exactitud",
            "dirs_hoja_trabajo_exactitud",
            "dirs_bitacoras_exactitud",
            "dirs_soportes_cromatográficos_exactitud",
        ],
        "data_extraction_model": Set4ExtractionModel,
        "structured_output_supervisor": Set4StructuredOutputSupervisor,
        "tags": ["activos_exactitud", "referencia_exactitud"],
    },
    "Set 5": {
        "human_message_prompt": RULES_SET_5,
        "doc_path_list": [
           # "dir_protocolo",
            "dir_reporte_lims_precision_sistema",
            #"dirs_hoja_trabajo_precision_sistema",
            #"dirs_bitacoras_precision_sistema",
            #"dirs_soportes_cromatograficos_precision_sistema",
        ],
        "data_extraction_model": Set5ExtractionModel,
        "structured_output_supervisor": Set5StructuredOutputSupervisor,
        "tags": ["activos_precision_sistema", "refencia_precision_sistema"],
    },
    "Set 6": {
        "human_message_prompt": RULES_SET_6,
        "doc_path_list": [
            "dir_protocolo",
            "dir_reporte_lims_precision_metodo",
            "dirs_hoja_trabajo_precision_metodo",
            "dirs_bitacoras_precision_metodo",
            "dirs_soportes_cromatograficos_precision_metodo",
        ],
        "data_extraction_model": Set6ExtractionModel,
        "structured_output_supervisor": Set6StructuredOutputSupervisor,
        "tags": ["activos_precision_metodo", "refencia_precision_metodo"],
    },
    "Set 7": {
        "human_message_prompt": RULES_SET_7,
        "doc_path_list": [
            "dir_protocolo",
            "dir_reporte_lims_precision_intermedia",
            "dirs_hoja_trabajo_precision_intermedia",
            "dirs_bitacoras_precision_intermedia",
            "dirs_soportes_cromatograficos_precision_intermedia",
        ],
        "data_extraction_model": Set7ExtractionModel,
        "structured_output_supervisor": Set7StructuredOutputSupervisor,
        "tags": ["activos_precision_intermedia", "refencia_precision_intermedia"],
    },
    "Set 8": {
        "human_message_prompt": RULES_SET_8,
        "doc_path_list": [
            "dir_protocolo",
            "dir_reporte_lims_estabilidad_solucion",
            #"dirs_hoja_trabajo_estabilidad_solucion",
            #"dirs_bitacoras_estabilidad_solucion",
            #"dirs_soportes_cromatograficos_estabilidad_solucion",
        ],
        "data_extraction_model": Set8ExtractionModel,
        "structured_output_supervisor": Set8StructuredOutputSupervisor,
        "tags": ["activos_estabilidad_solucion", "referencia_analitica_estabilidad_soluciones"],
    },
    "Set 10": {
        "human_message_prompt": RULES_SET_10,
        "doc_path_list": [
            "dir_protocolo",
            #"dir_reporte_lims_estabilidad_solucion_fase_movil",
            #"dirs_hoja_trabajo_estabilidad_solucion_fase_movil",
            #"dirs_bitacoras_estabilidad_solucion_fase_movil",
            "dirs_soportes_cromatograficos_estabilidad_solucion_fase_movil",
        ],
        "data_extraction_model": Set10ExtractionModel,
        "structured_output_supervisor": Set10StructuredOutputSupervisor,
        "tags": ["activos_estabilidad_solucion_fase_movil", "refencia_estabilidad_solucion_fase_movil"],
    },
    "Set 11": {
        "human_message_prompt": RULES_SET_11,
        "doc_path_list": [
            "dir_protocolo",
            "dir_reporte_lims_robustez",
            "dirs_hoja_trabajo_robustez",
            "dirs_bitacoras_robustez",
            "dirs_soportes_cromatograficos_robustez",
        ],
        "data_extraction_model": Set11ExtractionModel,
        "structured_output_supervisor": Set11StructuredOutputSupervisor,
        "tags": ["activos_robustez", "refencia_robustez"],
    },
}

TEMPLATE_SETS = {
    "Protocolo": TEMPLATE_SETS_TRIAL["Protocolo"],
    "Set 5": TEMPLATE_SETS_TRIAL["Set 5"]
}