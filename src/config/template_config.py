from src.config.models.set_1 import Set1ExtractionModel, Set1RenderingModel, Set1StructuredOutputSupervisor
from src.config.models.set_2 import Set2ExtractionModel, Set2RenderingModel, Set2StructuredOutputSupervisor
from src.config.models.set_3 import Set3ExtractionModel, Set3RenderingModel, Set3StructuredOutputSupervisor
from src.config.models.set_4 import Set4ExtractionModel, Set4RenderingModel, Set4StructuredOutputSupervisor
from src.config.models.set_5 import Set5ExtractionModel, Set5RenderingModel, Set5StructuredOutputSupervisor
from src.config.models.set_6 import Set6ExtractionModel, Set6RenderingModel, Set6StructuredOutputSupervisor

TEMPLATE_SETS = {
    "Set 1": {
        "human_message_prompt": "",
        "doc_path_list": ["validacion", "codigo_informe", "nombre_producto", "codigo_producto", "lista_activos", "rango_validado"],
        "data_extraction_model_key": Set1ExtractionModel,
        "data_rendering_model_key": Set1RenderingModel,
        "structured_output_supervisor": Set1StructuredOutputSupervisor,
        "tags": ["validacion", "codigo_informe", "nombre_producto", "codigo_producto", "lista_activos", "concentracion_activos", "rango_validado", "activos"],
    },
    "Set 2": {
        "human_message_prompt": "",
        "doc_path_list": ["dirs_hoja_trabajo_linealidad", "dirs_bitacoras_linealidad", "dirs_soportes_cromatográficos_linealidad", "dirs_hoja_trabajo_precision_sistema", "dirs_bitacoras_precision_sistema", "dirs_soportes_cromatográficos_precision_sistema", "dirs_hoja_trabajo_precision_metodo", "dirs_bitacoras_precision_metodo", "dirs_soportes_cromatográficos_precision_metodo", "dirs_hoja_trabajo_precision_intermedia", "dirs_bitacoras_precision_intermedia", "dirs_soportes_cromatográficos_precision_intermedia", "dirs_hoja_trabajo_exactitud", "dirs_bitacoras_exactitud", "dirs_soportes_cromatográficos_exactitud", "dirs_hoja_trabajo_estabilidad_solucion_estandar", "dirs_bitacoras_estabilidad_solucion_estandar", "dirs_soportes_cromatográficos_estabilidad_solucion_estandar", "dirs_hoja_trabajo_estabilidad_solucion_muestra", "dirs_bitacoras_estabilidad_solucion_muestra", "dirs_soportes_cromatográficos_estabilidad_solucion_muestra", "dirs_hoja_trabajo_estabilidad_solucion_fase_movil", "dirs_bitacoras_estabilidad_solucion_fase_movil", "dirs_soportes_cromatográficos_estabilidad_solucion_fase_movil", "dirs_hoja_trabajo_robustez", "dirs_bitacoras_robustez", "dirs_soportes_cromatográficos_robustez"],
        "data_extraction_model_key": Set2ExtractionModel,
        "data_rendering_model_key": Set2RenderingModel,
        "structured_output_supervisor": Set2StructuredOutputSupervisor,
        "tags": ["muestra_utilizadas", "estandar_utilizados", "reactivo_utilizados", "materiales_utilizados", "equipos_utilizados", "columna_utilizada"],
    },
    "Set 3": {
        "human_message_prompt": "",
        "doc_path_list": ["dir_reporte_lims_precision_sistema", "dirs_hoja_trabajo_linealidad", "dirs_bitacoras_linealidad", "dirs_soportes_cromatográficos_linealidad"],
        "data_extraction_model_key": Set3ExtractionModel,
        "data_rendering_model_key": Set3RenderingModel,
        "structured_output_supervisor": Set3StructuredOutputSupervisor,
        "tags": ["activos_linealidad", "referencia_linealidad"],
    },
    "Set 4": {
        "human_message_prompt": "",
        "doc_path_list": ["dir_reporte_lims_exactitud", "dirs_hoja_trabajo_exactitud", "dirs_bitacoras_exactitud", "dirs_soportes_cromatográficos_exactitud"],
        "data_extraction_model_key": Set4ExtractionModel,
        "data_rendering_model_key": Set4RenderingModel,
        "structured_output_supervisor": Set4StructuredOutputSupervisor,
        "tags": ["activos_exactitud", "referencia_exactitud"],
    },
    "Set 5": {
        "human_message_prompt": [],
        "doc_path_list": [],
        "data_extraction_model_key": Set5ExtractionModel,
        "data_rendering_model_key": Set5RenderingModel,
        "structured_output_supervisor": Set5StructuredOutputSupervisor,
        "tags": [],
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