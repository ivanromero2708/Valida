from src.config.models.set_1 import Set1ExtractionModel, Set1RenderingModel, Set1StructuredOutputSupervisor
from src.config.models.set_2 import Set2ExtractionModel, Set2RenderingModel, Set2StructuredOutputSupervisor
from src.config.models.set_3 import Set3ExtractionModel, Set3RenderingModel, Set3StructuredOutputSupervisor
from src.config.models.set_4 import Set4ExtractionModel, Set4RenderingModel, Set4StructuredOutputSupervisor
from src.config.models.set_5 import Set5ExtractionModel, Set5RenderingModel, Set5StructuredOutputSupervisor
from src.config.models.set_6 import Set6ExtractionModel, Set6RenderingModel, Set6StructuredOutputSupervisor

TEMPLATE_SETS = {
    "Set 1": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set1ExtractionModel,
        "data_rendering_model_key": Set1RenderingModel,
        "structured_output_supervisor": Set1StructuredOutputSupervisor,
        "tags": ["validacion", "codigo_informe", "nombre_producto", "codigo_producto", "lista_activos", "concentracion_activos", "rango_validado", "activos"],
    },
    "Set 2": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set2ExtractionModel,
        "data_rendering_model_key": Set2RenderingModel,
        "structured_output_supervisor": Set2StructuredOutputSupervisor,
        "tags": ["introduccion"],
    },
    "Set 3": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set3ExtractionModel,
        "data_rendering_model_key": Set3RenderingModel,
        "structured_output_supervisor": Set3StructuredOutputSupervisor,
        "tags": ["codigo_protocolo_validacion", "nombre_del_protocolo_validacion", "parametros_de_validacion"],
    },
    "Set 4": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set4ExtractionModel,
        "data_rendering_model_key": Set4RenderingModel,
        "structured_output_supervisor": Set4StructuredOutputSupervisor,
        "tags": ["muestra_utilizadas", "estandar_utilizados", "reactivo_utilizados", "materiales_utilizados", "equipos_utilizados"],
    },
    "Set 5": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set5ExtractionModel,
        "data_rendering_model_key": Set5RenderingModel,
        "structured_output_supervisor": Set5StructuredOutputSupervisor,
        "tags": ["activos", "precision_sistema", "criterio_precision_sistema", "RSD_precision_pico_1_precision_sistema", "RSD_precision_pico_2_precision_sistema", "RSD_precision_pico_3_precision_sistema", "RSD_precision_pico_4_precision_sistema", "RSD_precision_pico_5_precision_sistema", "precision_metodo", "RSD_precision_pico_1_precision_metodo", "RSD_precision_pico_2_precision_metodo", "RSD_precision_pico_3_precision_metodo", "RSD_precision_pico_4_precision_metodo", "RSD_precision_pico_5_precision_metodo", "CONC_precision_pico_1_precision_metodo", "CONC_precision_pico_2_precision_metodo", "CONC_precision_pico_3_precision_metodo", "CONC_precision_pico_4_precision_metodo", "CONC_precision_pico_5_precision_metodo", "criterio_rsd_max_num", "conclusion_global_precision_metodo", "precision_intermedia", "rsd_por_activo", "conclusion_global", "criterio_txt_precision_intermedia", "estbilidad_sol_std", "activosestbilidad_sol_std", "estbilidad_sol_std", "criterio_txt_estabilidad_solucion", "concl_T1C1", "concl_T1C2", "concl_T2C1", "concl_T2C2", "concl_T3C1", "concl_T3C2", "estbilidad_sol_mta", "criterio_txt_estabilidad_sol_mta"],
    },
    "Set 6": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set6ExtractionModel,
        "data_rendering_model_key": Set6RenderingModel,
        "structured_output_supervisor": Set6StructuredOutputSupervisor,
        "tags": ["columna_utilizada"],
    },
}