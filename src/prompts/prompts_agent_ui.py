HUMAN_MESSAGE_PROMPT = """
A continuación se encuentran todas las particularidades y reglas para razonamiento y salida estructurada de forma vinculante para este proceso:
- Modelo de impresión: <STRUCTURED_OUTPUT_SUPERVISOR>{structured_output_supervisor}</STRUCTURED_OUTPUT_SUPERVISOR>
- Tags a generar al final del proceso: <TAGS>{tags}</TAGS>
- Reglas de razonamiento: <REGLAS_DE_RAZONAMIENTO>{reglas_razonamiento}</REGLAS_DE_RAZONAMIENTO>
- Contexto para el set: <CONTEXT_DATA_JSON_STR>{context_data_json_str}</CONTEXT_DATA_JSON_STR>
"""
