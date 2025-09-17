RULES_SET_1 = """


"""

RULES_SET_2 = """


"""

RULES_SET_3 = """
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al agente de extracción estructurada (`structured_extraction_agent`).

  - **Objetivo**: Extraer los datos de validación para el parámetro de **linealidad** de cada ingrediente activo (API) a partir de los documentos proporcionados (reportes LIMS, protocolos de validación) y estructurarlos según el modelo `Set3ExtractionModel`.

  - **Plan de Acción Iterativo**:

    1.  **Identificar APIs**: Primero, realiza una consulta al `vectorstore` para listar todos los ingredientes activos que tienen datos de linealidad en los reportes LIMS.
    2.  **Extracción por API**: Para cada ingrediente activo identificado, ejecuta un ciclo de consultas enfocadas para poblar el modelo `ParametroLinealidadExtraccion`:
          * **Consulta 1 (Tabla de Linealidad)**: Extrae los datos tabulares de linealidad del sistema (`linealidad_sistema`).
          * **Consulta 2 (Parámetros de Regresión)**: Extrae los valores individuales como `rsd_factor`, `pendiente`, `intercepto`, `r`, `r2` y `porcentaje_intercepto`.
          * **Consulta 3 (Criterios de Aceptación)**: Extrae los `criterio_linealidad` del protocolo de validación.
          * **Consulta 4 (Referencias)**: Localiza y extrae los códigos de referencia (`referencia_linealidad`) asociados a los datos brutos.
    3.  **Trazabilidad**: Asegúrate de que cada pieza de información extraída mantenga una referencia a su documento de origen (ej. "Reporte LIMS", "Protocolo de Validación").

  - **Ejemplo de Extracción Estructurada**:

    ```json
    {
      "activos_linealidad": [
        {
          "nombre": "[NOMBRE_DEL_API_1]",
          "linealidad_sistema": [
            { "nivel": "I (50%)", "concentracion": 0.06, "area_pico": 150000, "factor_respuesta": 2500000 },
            { "nivel": "II (75%)", "concentracion": 0.09, "area_pico": 225000, "factor_respuesta": 2500000 },
            { "nivel": "III (100%)", "concentracion": 0.12, "area_pico": 300000, "factor_respuesta": 2500000 },
            { "nivel": "IV (125%)", "concentracion": 0.15, "area_pico": 375000, "factor_respuesta": 2500000 },
            { "nivel": "V (150%)", "concentracion": 0.18, "area_pico": 450000, "factor_respuesta": 2500000 }
          ],
          "rsd_factor": 1.5,
          "pendiente": 2500000,
          "intercepto": 1000,
          "r": 0.9999,
          "r2": 0.9998,
          "porcentaje_intercepto": 1.2,
          "criterio_linealidad": [
            { "parametro": "Coeficiente de correlación (r)", "criterio": "≥ 0.995" },
            { "parametro": "RSD de los factores de respuesta", "criterio": "≤ 2.0%" },
            { "parametro": "Intercepto como porcentaje", "criterio": "≤ 2.0%" }
          ]
        }
      ],
      "referencia_linealidad": ["[HT001XXXXXX]"]
    }
    ```
</REGLAS_DE_EXTRACCION_ESTRUCTURADA>


<REGLAS_DE_RAZONAMIENTO>
Estas reglas aplican al agente de razonamiento (`reasoning_agent`).

  - **Regla Principal**: Para cada ingrediente activo, debes comparar los valores extraídos (`rsd_factor`, `r`, `porcentaje_intercepto`, etc.) con sus correspondientes `criterio_linealidad` para determinar si se cumple la validación.

  - **Orden Estricto**: El **razonamiento siempre debe preceder a la conclusión**. Documenta explícitamente la comparación antes de determinar el estado de cumplimiento.

  - **Pasos del Razonamiento**:

    1.  **Iterar por Parámetro**: Para cada criterio de aceptación definido en `criterio_linealidad`, realiza y documenta la comparación con el valor extraído del reporte LIMS.
    2.  **Verificación Individual**: Indica si cada parámetro individual cumple o no con su criterio.
    3.  **Conclusión Global**: Basado en las verificaciones individuales, determina el estado global (`cumple_global`) para el ingrediente activo. Si al menos un criterio no se cumple, el resultado global es "No Cumple".
    4.  **Justificación Explícita**: Registra el porqué de la decisión final, resumiendo las comparaciones.

  - **Ejemplo de Razonamiento Detallado**:

      - **API**: `[NOMBRE_DEL_API_1]`
      - **Verificación 1 (Coeficiente de correlación)**: El valor extraído `r` es `0.9999`. El criterio de aceptación es `≥ 0.995`. **Razonamiento**: `0.9999` es mayor que `0.995`, por lo tanto, este parámetro **Cumple**.
      - **Verificación 2 (RSD de factores de respuesta)**: El valor extraído `rsd_factor` es `1.5%`. El criterio es `≤ 2.0%`. **Razonamiento**: `1.5%` es menor o igual a `2.0%`, por lo tanto, este parámetro **Cumple**.
      - **Verificación 3 (Porcentaje de intercepto)**: El valor extraído `porcentaje_intercepto` es `1.2%`. El criterio es `≤ 2.0%`. **Razonamiento**: `1.2%` es menor o igual a `2.0%`, por lo tanto, este parámetro **Cumple**.
      - **Justificación de la Conclusión Global**: Todos los parámetros evaluados (coeficiente de correlación, RSD de los factores de respuesta y porcentaje de intercepto) se encuentran dentro de los límites establecidos por los criterios de aceptación.
</REGLAS_DE_RAZONAMIENTO>

<REGLAS_DE_SALIDA_SUPERVISOR>
Estas reglas aplican al `supervisor` para generar la salida final.

  - **Modelo de Salida**: La salida final debe ser un objeto JSON bien formado que siga estrictamente la estructura del modelo `Set3StructuredOutputSupervisor`. No incluyas texto, explicaciones ni bloques de código adicionales.

  - **Integración de Datos**: La salida debe combinar la información extraída (datos brutos y criterios) con las conclusiones generadas durante el razonamiento (el campo `cumple_global`).

  - **Restricción Clave**: Recuerda, la conclusión (`cumple_global`) que se reporta en esta salida final debe haber sido justificada previamente en el paso de razonamiento.

  - **Ejemplo de Salida del Supervisor**:

    ```json
    {
      "activos_linealidad": [
        {
          "nombre": "[NOMBRE_DEL_API_1]",
          "linealidad_sistema": [
            { "nivel": "I (50%)", "concentracion": 0.06, "area_pico": 150000, "factor_respuesta": 2500000 },
            { "nivel": "II (75%)", "concentracion": 0.09, "area_pico": 225000, "factor_respuesta": 2500000 },
            { "nivel": "III (100%)", "concentracion": 0.12, "area_pico": 300000, "factor_respuesta": 2500000 },
            { "nivel": "IV (125%)", "concentracion": 0.15, "area_pico": 375000, "factor_respuesta": 2500000 },
            { "nivel": "V (150%)", "concentracion": 0.18, "area_pico": 450000, "factor_respuesta": 2500000 }
          ],
          "rsd_factor": 1.5,
          "pendiente": 2500000,
          "intercepto": 1000,
          "r": 0.9999,
          "r2": 0.9998,
          "porcentaje_intercepto": 1.2,
          "cumple_global": "Cumple",
          "criterio_linealidad": [
            { "parametro": "Coeficiente de correlación (r)", "criterio": "≥ 0.995" },
            { "parametro": "RSD de los factores de respuesta", "criterio": "≤ 2.0%" },
            { "parametro": "Intercepto como porcentaje", "criterio": "≤ 2.0%" }
          ]
        }
      ],
      "referencia_linealidad": ["[HT001XXXXXX]"]
    }
    ```
</REGLAS_DE_SALIDA_SUPERVISOR>
"""
RULES_SET_4 = """


"""

RULES_SET_5 = """


"""

RULES_SET_6 = """


"""

RULES_SET_7 = """


"""

RULES_SET_8 = """


"""

RULES_SET_9 = """


"""

RULES_SET_10 = """


"""

RULES_SET_11 = """


"""

