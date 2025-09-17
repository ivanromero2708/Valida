HUMAN_MESSAGE_PROMPT = """
A continuación se encuentran todas las particularidades y reglas para extracción y razonamiento de forma vinculante para este proceso.. El supervisor deberá distribuir cada una de estas reglas en cada uno de sus agentes:

- Reglas de extracción y razonamiento: <REGLAS_DE_EXTRACCION_RAZONAMIENTO>{reglas_extraccion_razonamiento}</REGLAS_DE_EXTRACCION_RAZONAMIENTO>
- Tags a generar al final del proceso: <TAGS>{tags}</TAGS>.
- Lista de directorios locales de los documentos a procesar: <LISTA_DOCS>{doc_path_list}</LISTA_DOCS>
"""
