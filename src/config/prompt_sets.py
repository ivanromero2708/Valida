RULES_SET_2 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al agente de extracción estructurada (`structured_extraction_agent`).

    - **Objetivo General:** Extraer y estructurar la información de muestras, estándares, reactivos, materiales, equipos y columnas, diferenciando entre lo especificado en el protocolo de validación y lo documentado en las hojas de trabajo.

    - **Fase 1: Extracción de Requisitos del Protocolo de Validación**

        - **Fuente:** El documento principal del protocolo de validación.
        - **Objetivo Específico:** Identificar y listar todos los elementos *requeridos* o *especificados* para el análisis.
        - **Plan de Acción:**
          1.  **Muestras y Estándares:** Realiza consultas buscando "Muestras", "Productos", "Estándares" y los nombres de los principios activos (API). Extrae los nombres de los productos y los estándares mencionados.
          2.  **Reactivos:** Realiza consultas buscando "Reactivos", "Solución Amortiguadora", "Fase Móvil" y nombres de químicos. Lista todos los reactivos especificados.
          3.  **Equipos:** Realiza consultas buscando "Equipos". Extrae la lista de equipos genéricos requeridos.
          4.  **Columna Cromatográfica:** Realiza consultas específicas buscando "Columna", "Condiciones Cromatográficas". Extrae la descripción completa de la columna, incluyendo fabricante, dimensiones y número de parte.
        - **Salida de Fase 1 (Población de campos `_protocolo`):**
            - `muestra_utilizadas_protocolo`: ["[Nombre del Producto] [Concentración]"]
            - `estandar_utilizados_protocolo`: ["[API_Principal_Estándar_Farmacopea]", "[API_Secundario_Estándar_de_Trabajo]"]
            - `reactivo_utilizados_protocolo`: ["Buffer de Fosfato", "Agua grado HPLC", "Metanol", "Ácido Fosfórico"]
            - `equipos_utilizados_protocolo`: ["Sistema HPLC con detector DAD", "Balanza Analítica", "pH-metro"]
            - `columna_utilizada_protocolo`: ["Waters Symmetry C18 (150 x 3.9) mm 5µm, Número de parte: WAT046980"]
        - Es importante que reportes los listados de la información identificada aquí.

    - **Fase 2: Extracción de Datos de Ejecución de Hojas de Trabajo y Bitácoras**

        - **Fuentes:** Las hojas de trabajo, bitácoras de preparación y registros de análisis.
        - **Objetivo Específico:** Extraer los detalles (lotes, códigos, series, etc.) de los elementos *realmente utilizados* durante la ejecución del análisis.
        - **Plan de Acción:**
          1.  **Muestras:** Busca tablas de "IDENTIFICACIÓN DE LA MUESTRA" para extraer "Nombre del material", "Código", "Lote(s)/CIM".
          2.  **Estándares:** Busca tablas de "INFORMACION DE ESTANDARES" para extraer "Nombre", "Lote", "Fabricante", "Código", "Potencia", "Vigencia".
          3.  **Reactivos:** Busca tablas de "REACTIVOS EMPLEADOS" para extraer "Nombre", "Lote", "Fabricante", "Fecha Vencimiento", "\#Parte".
          4.  **Materiales:** Busca en el texto y tablas referencias a materiales consumibles como "filtro de jeringa", "membrana de nylon", "viales". Extrae cualquier detalle disponible como tipo, tamaño de poro, fabricante o lote.
          5.  **Equipos:** Busca tablas de "EQUIPOS UTILIZADOS" y registros de pesaje para extraer "Nombre del Equipo/No.", "ID de balanza", "Fabricante", "Modelo", "N.º ser.", "Fecha de próxima calificación/calibración".
          6.  **Columnas:** Busca en las notas o registros de corridas cromatográficas detalles de la columna utilizada, como su número de serie o identificador interno.
        - **Salida de Fase 2 (Población de campos principales):** Rellena la estructura JSON principal con todos los datos extraídos de las hojas de trabajo, creando un objeto por cada ítem único identificado.

    - **Normalización Mínima:**

        - Trim y colapso de espacios; preservar acentos y mayúsculas/minúsculas originales.
        - No alterar el formato de fechas, códigos o números de serie. No inventar valores; si un dato no está presente, dejar el campo como nulo o una cadena vacía.

  -----

  **Nota Importante:** El siguiente bloque de código es un **ejemplo sintético** para ilustrar la estructura de salida de la extracción. **Por ningún motivo debe ser tomado como una salida real de los agentes.**

  -----

    - **Ejemplo de Extracción Estructurada Completa (plantilla Set2ExtractionModel):**
      ```json
      {
        "muestra_utilizadas_protocolo": [
          "Producto Analizado XYZ 50mg/5mL Solución Oral"
        ],
        "estandar_utilizados_protocolo": [
          "API-XYZ Estándar de Referencia USP"
        ],
        "reactivo_utilizados_protocolo": [
          "Metanol Grado HPLC", "Buffer de Fosfatos pH 3.0"
        ],
        "materiales_utilizados_protocolo": [
          "Filtros de jeringa 0.22 µm PVDF"
        ],
        "equipos_utilizados_protocolo": [
          "Sistema HPLC", "Balanza Analítica con 0.01mg de precisión"
        ],
        "columna_utilizada_protocolo": [
          "Waters Symmetry C18 (150 x 3.9) mm 5µm, Número de parte: WAT046980"
        ],
        "muestra_utilizadas": [
          { "nombre": "Producto Analizado XYZ", "codigo": "FG-102030", "lote": "LOTE-PILOTO-001", "codigo_interno_cim": "CI-25-001-LAB" }
        ],
        "estandar_utilizados": [
          { "nombre": "API-XYZ Estándar", "fabricante": "USP", "lote": "R098W0", "numero_parte": null, "codigo_identificacion": "USP-1044331", "potencia": "99.5% (base seca)", "vencimiento": "2026-08-31" }
        ],
        "reactivo_utilizados": [
          { "nombre": "Metanol", "fabricante": "J.T.Baker", "lote": "24599103", "numero_parte": "9093-33", "vencimiento": "2027-01-31" }
        ],
        "materiales_utilizados": [
          { "nombre": "Filtro de jeringa PVDF", "fabricante": "Millipore", "numero_parte": "SLGV033RS", "lote": "R5AA4411" }
        ],
        "equipos_utilizados": [
          { "nombre": "Balanza", "consecutivo": "BAL-AN-04", "fabricante": "Mettler Toledo", "modelo": "XP205", "serial": "B512345678", "prox_actividad": "2026-03-31" }
        ],
        "columna_utilizada": [
          { "descripcion": "Waters Symmetry C18 5µm 150x3.9mm", "fabricante": "Waters", "numero_parte": "WAT046980", "serial": "018834215132", "numero_interno": "COL-HPLC-112" }
        ]
      }
      ```

  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  **Objetivo Principal:** Estandarizar y consolidar la información de materiales, reactivos y equipos utilizados en un análisis. El objetivo es corregir los nombres registrados en las hojas de trabajo (`*_utilizados`) para que coincidan con los nombres oficiales del protocolo (`*_utilizados_protocolo`), pero conservando toda la información detallada (lotes, identificadores, fechas, etc.) registrada en la hoja de trabajo.

  **IMPORTANTE**: NO VAS A USAR NINGUNA HERRAMIENTA DE GRAFICADO.

  **Entradas:**
  1.  **Listas del Protocolo (`*_utilizados_protocolo`):** Contienen los nombres oficiales y canónicos para cada categoría (reactivos, estándares, materiales, equipos, columnas). Esta es la fuente de la verdad para los nombres.
  2.  **Listas de las Hojas de Trabajo (`*_utilizados`):** Contienen la información de uso real, incluyendo detalles como número de lote, ID interno, fechas, etc. Los nombres en estas listas pueden tener errores tipográficos, abreviaturas o variaciones.

  **Pasos de Ejecución:**

  1.  **Iterar por Categoría:** Procesa secuencialmente cada categoría de ítem (Reactivos, Estándares, Equipos, Columnas, etc.).

  2.  **Mapeo por Similitud (Matching):**
      * Para cada ítem en la lista de la hoja de trabajo (`*_utilizados`), busca la correspondencia más lógica y cercana en la lista del protocolo (`*_utilizados_protocolo`).
      * Utiliza un criterio de coincidencia flexible (fuzzy string matching) para resolver discrepancias como errores de tipeo, abreviaturas o palabras faltantes. Por ejemplo, "Ac. Fosforico" en la hoja de trabajo debería coincidir con "Ácido Fosfórico 85%" en el protocolo.

  3.  **Consolidación de Datos:**
      * Una vez que encuentres una coincidencia, crea un nuevo registro consolidado.
      * Este registro **DEBE** usar el **nombre oficial** extraído de la lista del **protocolo**.
      * Este registro **DEBE** conservar **TODA la información adicional** (ej: `lote`, `ID_equipo`, `fecha_vencimiento`, `cantidad_usada`) que venía con el ítem en la lista de la **hoja de trabajo**.

  4.  **Generación de Salida Final:**
      * El resultado final debe ser una única lista consolidada por cada categoría.
      * En estas listas finales, todos los nombres deben ser los oficiales del protocolo, y la información asociada a cada nombre debe ser la que se registró en la ejecución (hojas de trabajo).
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_SUPERVISOR>
  Estas reglas aplican al `supervisor` para la generación de la salida final.

    - **Modelo de Salida:** La salida debe ser **únicamente** un objeto JSON bien formado que se adhiera a la estructura `Set2StructuredOutputSupervisor`. No incluyas texto, explicaciones o marcadores de código adicionales.

    - **Condición de Emisión:** Genera la salida JSON **solo después** de que el agente de razonamiento haya completado y documentado su proceso de reconciliación y consolidación.

    - **Contenido de la Salida:** El JSON final debe contener las listas de ítems ya resueltas, deduplicadas y verificadas. Los campos `*_utilizados_protocolo` no deben incluirse en la salida final, ya que representan información intermedia utilizada durante el razonamiento.

  -----

  **Nota Importante:** El siguiente bloque de código es un **ejemplo sintético** para ilustrar la estructura de salida del supervisor. **Por ningún motivo debe ser tomado como una salida real de los agentes.**

  -----

    - **Ejemplo de Salida del Supervisor (plantilla Set2StructuredOutputSupervisor):**
      ```json
      {
        "muestra_utilizadas": [
          {
            "nombre": "Producto Analizado XYZ 50mg/5mL Solución Oral",
            "codigo": "FG-102030",
            "lote": "LOTE-PILOTO-001",
            "codigo_interno_cim": "CI-25-001-LAB"
          }
        ],
        "estandar_utilizados": [
          {
            "nombre": "API-XYZ Estándar de Referencia",
            "fabricante": "USP",
            "lote": "R098W0",
            "numero_parte": null,
            "codigo_identificacion": "USP-1044331",
            "potencia": "99.5% (base seca)",
            "vencimiento": "2026-08-31"
          }
        ],
        "reactivo_utilizados": [
          {
            "nombre": "Metanol Grado HPLC",
            "fabricante": "J.T.Baker",
            "lote": "24599103",
            "numero_parte": "9093-33",
            "vencimiento": "2027-01-31"
          },
          {
            "nombre": "Fosfato de Potasio Monobásico",
            "fabricante": "Merck",
            "lote": "A31B456",
            "numero_parte": "1.04873.1000",
            "vencimiento": "2028-12-31"
          },
          {
            "nombre": "Agua Grado HPLC",
            "fabricante": null,
            "lote": null,
            "numero_parte": null,
            "vencimiento": null
          }
        ],
        "materiales_utilizados": [
          {
            "nombre": "Filtro de jeringa 0.22 µm PVDF",
            "fabricante": "Millipore",
            "numero_parte": "SLGV033RS",
            "lote": "R5AA4411"
          }
        ],
        "equipos_utilizados": [
          {
            "nombre": "Sistema HPLC",
            "consecutivo": "HPLC-08",
            "fabricante": "Agilent",
            "modelo": "1260 Infinity II",
            "serial": "DE12345678",
            "prox_actividad": "2026-06-30"
          },
          {
            "nombre": "Balanza Analítica",
            "consecutivo": "BAL-AN-04",
            "fabricante": "Mettler Toledo",
            "modelo": "XP205",
            "serial": "B512345678",
            "prox_actividad": "2026-03-31"
          }
        ],
        "columna_utilizada": [
          {
            "descripcion": "Waters Symmetry C18 (150 x 3.9) mm 5µm",
            "fabricante": "Waters",
            "numero_parte": "WAT046980",
            "serial": "018834215132",
            "numero_interno": "COL-HPLC-112"
          }
        ]
      }
      ```
  </REGLAS_DE_SALIDA_SUPERVISOR>
"""

RULES_SET_3 = """
  `<REGLAS_DE_EXTRACCION_ESTRUCTURADA>`
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer los criterios de aceptación para **linealidad** desde el protocolo de validación y los datos experimentales (curva de calibración y parámetros de regresión) desde los reportes LIMS, estructurando la información según el modelo `Set3ExtractionModel`.

  -----

    - **Fase 1: Extracción de Criterios de Aceptación desde el Protocolo**

        - **Fuente Primaria:** Vectorstore .parquet del Documento del **Protocolo de Validación**.
        - **Objetivo Específico:** Identificar y listar todos los criterios de aceptación definidos para el parámetro de linealidad.
        - **Plan de Acción:**
          1.  **Enfócate en el protocolo.** Realiza búsquedas específicas en el documento usando términos como "Linealidad", "Criterios de Aceptación", "Coeficiente de correlación", "r²", "Intercepto", "Factor de respuesta".
          2.  **Busca la tabla de criterios.** La linealidad suele tener múltiples criterios. Busca una tabla o lista que defina los límites para cada uno (ej: `r ≥ 0.995`, `RSD ≤ 2.0%`).
          3.  **Extrae todos los criterios.** Captura cada par de "parámetro" y "criterio" encontrado y puebla la lista `criterio_linealidad`.
        - **Salida de Fase 1 (Ejemplo):**
          ```json
          {
            "activos_linealidad": [
              {
                "nombre": "[NOMBRE_DEL_API_1]",
                "criterio_linealidad": "[CRITERIO_LINEALIDAD_API_1]",
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de Datos de Ejecución desde el Reporte LIMS**

        - **Fuente Primaria:** Reporte de datos crudos del **LIMS** o la **Hoja de Trabajo Analítica**.
        - **Objetivo Específico:** Extraer la curva de calibración completa (todos los niveles con **todas sus réplicas**) y los parámetros de regresión calculados por el software.
        - **Plan de Acción:**
          1.  **Extrae la curva de calibración completa.** Busca la tabla principal de datos de linealidad. Debe contener columnas como "Nivel", "Concentración", "Réplica", "Área de Pico", y "Factor de Respuesta". **Es crucial que extraigas una entrada por cada inyección/réplica individual**, no un promedio por nivel.
          2.  **Extrae los parámetros de regresión.** Usualmente, debajo de la tabla de datos, el software reporta los resultados del ajuste lineal. Busca y extrae los valores numéricos para `pendiente`, `intercepto`, `r` (coeficiente de correlación), `r2` (coeficiente de determinación).
          3.  **Extrae los cálculos de resumen.** Busca valores calculados adicionales como el `rsd_factor` (RSD de los factores de respuesta) y el `porcentaje_intercepto`.
          4.  **Extrae la referencia.** Identifica el código de la corrida o de la hoja de trabajo (ej. "HT-...") y asígnalo a `referencia_linealidad`.

    - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
      *NOTA: Este ejemplo ahora muestra múltiples réplicas por nivel, como solicitaste.*

      ```json
      {
        "activos_linealidad": [
          {
            "nombre": "[NOMBRE_DEL_API_1]",
            "linealidad_sistema": [
              { "nivel": "I (50%)", "replica": 1, "concentracion": 0.06, "area_pico": 150100 },
              { "nivel": "I (50%)", "replica": 2, "concentracion": 0.06, "area_pico": 149900 },
              { "nivel": "II (75%)", "replica": 1, "concentracion": 0.09, "area_pico": 225300 },
              { "nivel": "II (75%)", "replica": 2, "concentracion": 0.09, "area_pico": 224700 },
              { "nivel": "III (100%)", "replica": 1, "concentracion": 0.12, "area_pico": 300500 },
              { "nivel": "III (100%)", "replica": 2, "concentracion": 0.12, "area_pico": 299500 },
              { "nivel": "IV (125%)", "replica": 1, "concentracion": 0.15, "area_pico": 375600 },
              { "nivel": "IV (125%)", "replica": 2, "concentracion": 0.15, "area_pico": 374400 },
              { "nivel": "V (150%)", "replica": 1, "concentracion": 0.18, "area_pico": 450800 },
              { "nivel": "V (150%)", "replica": 2, "concentracion": 0.18, "area_pico": 449200 }
            ],
            "rsd_factor": 1.5,
            "pendiente": 2500000,
            "intercepto": 1000,
            "r": 0.9999,
            "r2": 0.9998,
            "porcentaje_intercepto": 1.2,
            "criterio_linealidad": "[CRITERIO_LINEALIDAD_API_1]"
          }
        ],
        "referencia_linealidad": ["[HT001XXXXXX]"]
      }
      ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  <br>

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Comparar sistemáticamente cada parámetro de regresión extraído contra su criterio de aceptación correspondiente para emitir una conclusión global sobre la linealidad del método.

    - **Entradas:** El objeto JSON completo poblado por el `structured_extraction_agent`.

    - **Pasos del Razonamiento:**

      1.  **Iterar por Criterio:** Para cada parámetro en la lista `criterio_linealidad`, busca el valor experimental correspondiente (ej: si `parametro` es "Coeficiente de correlación (r)", busca el valor de `r`).
      2.  **Documentar Comparación:** Realiza y documenta la comparación numérica de forma explícita.
            - **Ejemplo 1:** *Verificación (r): Valor obtenido `r = 0.9999`. Criterio `≥ 0.995`. Comparación: `0.9999 ≥ 0.995` es VERDADERO. → Cumple.*
            - **Ejemplo 2:** *Verificación (RSD): Valor obtenido `rsd_factor = 1.5%`. Criterio `≤ 2.0%`. Comparación: `1.5 ≤ 2.0` es VERDADERO. → Cumple.*
      3.  **Conclusión Global:** Emite una conclusión para `cumple_global`.
            - Si **TODOS** los parámetros individuales cumplen su criterio → **"Cumple"**.
            - Si **AL MENOS UNO** de los parámetros no cumple su criterio → **"No Cumple"**.
      4.  **Justificación Final:** Proporciona un resumen que justifique la conclusión global, mencionando qué parámetros cumplieron o no.

  `</REGLAS_DE_RAZONAMIENTO>`

  <br>

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para generar la salida final.

    - **Modelo de Salida:** Un único objeto JSON que se adhiere estrictamente al modelo `Set3StructuredOutputSupervisor`. No incluyas texto o explicaciones fuera del JSON.

    - **Condición:** Genera la salida **solo después** de que el `reasoning_agent` haya documentado su análisis completo.

    - **Integración de Datos:** El JSON final debe contener los datos experimentales (`linealidad_sistema`, `r`, `pendiente`, etc.), los criterios (`criterio_linealidad`) y la conclusión final validada (`cumple_global`).

    - **Ejemplo de Salida del Supervisor (Caso "Cumple" con réplicas):**

      ```json
      {
        "activos_linealidad": [
          {
            "nombre": "[NOMBRE_DEL_API_1]",
            "linealidad_sistema": [
              { "nivel": "I (50%)", "replica": 1, "concentracion": 0.06, "area_pico": 150100 },
              { "nivel": "I (50%)", "replica": 2, "concentracion": 0.06, "area_pico": 149900 },
              { "nivel": "II (75%)", "replica": 1, "concentracion": 0.09, "area_pico": 225300 },
              { "nivel": "II (75%)", "replica": 2, "concentracion": 0.09, "area_pico": 224700 }
              // ... resto de los niveles y réplicas
            ],
            "rsd_factor": 1.5,
            "pendiente": 2500000,
            "intercepto": 1000,
            "r": 0.9999,
            "r2": 0.9998,
            "porcentaje_intercepto": 1.2,
            "cumple_global": "Cumple",
            "criterio_linealidad": "Coeficiente de correlación (r) criterio": "≥ 0.995"
          }
        ],
        "referencia_linealidad": ["[HT001XXXXXX]"]
      }
      ```
  `</REGLAS_DE_SALIDA_SUPERVISOR>`
"""

RULES_SET_4 = """
  `<REGLAS_DE_EXTRACCION_ESTRUCTURADA>`
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer el criterio de aceptación para **exactitud** desde el protocolo de validación y los datos de recuperación experimentales desde los reportes LIMS, estructurando la información final según el modelo `Set4ExtractionModel`.

  -----

    - **Fase 1: Extracción del Criterio de Aceptación desde el Protocolo**

        - **Fuente Primaria:** Documento del **Protocolo de Validación**.
        - **Objetivo Específico:** Identificar y extraer el criterio de aceptación para el porcentaje de recuperación (% recobro).
        - **Plan de Acción:**
          1.  **Enfócate en el protocolo.** Realiza búsquedas específicas en el documento usando términos clave como "Exactitud", "Accuracy", "Criterio de Aceptación", "Recuperación", "% Recovery", o "Recobro".
          2.  **Busca el rango de aceptación.** El criterio generalmente se expresa como un rango de porcentaje. Por ejemplo: "El promedio de la recuperación debe encontrarse en el rango de 98.0% a 102.0%". Extrae este texto completo.
          3.  **Puebla el campo de criterio.** Asigna el criterio extraído al campo `criterio_exactitud` para cada API relevante.
        - **Salida de Fase 1 (Ejemplo):**
          ```json
          {
            "activos_exactitud": [
              {
                "nombre": "[api_1_nombre]",
                "criterio_exactitud": "El % de recuperación debe estar entre 98.0% y 102.0%",
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de Datos de Recuperación desde el Reporte LIMS**

        - **Fuente Primaria:** Reporte de datos crudos del **LIMS** o la **Hoja de Trabajo Analítica**.
        - **Objetivo Específico:** Extraer todos los valores individuales de porcentaje de recuperación para cada nivel de concentración analizado.
        - **Plan de Acción:**
          1.  **Busca la tabla de resultados de exactitud.** Identifica tablas con títulos como "Accuracy", "Exactitud" o "Recuperación". Estas tablas deben contener columnas como "Nivel" (ej. "Level I", "80%"), "Réplica" y "% Recuperación" (o "% Recovery").
          2.  **Extrae todas las réplicas.** Es fundamental que extraigas una entrada por cada réplica o preparación individual. No debes promediar los valores en esta etapa. Puebla la lista `exactitud_metodo`.
          3.  **Extrae la referencia.** Localiza el identificador único del análisis o reporte (ej. "RUN-00123", "HTA-456") y asígnalo a `referencia_exactitud`.
        - **Normalización de Datos:**
            - `nivel`: Mantén la etiqueta original del reporte (ej: "Level I", "Nivel 80%").
            - `recuperacion`: Convierte el valor a tipo flotante (`float`), asegurando que la coma decimal sea un punto.

  -----

    - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
    **OJO, EN EL EJEMPLO APENAS APARECE UNA RÉPLICA POR CADA NIVEL, PERO ESTO ES SÓLO A MODO DE EJEMPLO.. NECESITO QUE EXTRAIGAS TODA LA DATA, ES DECIR, TODAS LAS REPLICAS POR CADA NIVEL**
      ```json
      {
        "activos_exactitud": [
          {
            "nombre": "[api_1_nombre]",
            "exactitud_metodo": [
              { "nivel": "Level I", "recuperacion": 99.2 },
              { "nivel": "Level I", "recuperacion": 100.3 },
              { "nivel": "Level I", "recuperacion": 99.8 },
              { "nivel": "Level II", "recuperacion": 100.1 },
              { "nivel": "Level II", "recuperacion": 101.5 },
              { "nivel": "Level II", "recuperacion": 100.9 },
              { "nivel": "Level III", "recuperacion": 98.7 },
              { "nivel": "Level III", "recuperacion": 99.1 },
              { "nivel": "Level III", "recuperacion": 98.9 }
            ],
            "conclusion_exactitud": "[pendiente_validar]",
            "criterio_exactitud": "El % de recuperación debe estar entre 98.0% y 102.0%"
          }
        ],
        "referencia_exactitud": "[lims_run_o_ref_analitica]"
      }
      ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Verificar si el porcentaje de recuperación promedio por cada nivel se encuentra dentro del criterio encontrado en el protocolo de validación.

    - **Entradas:** El objeto JSON completo del `structured_extraction_agent`.

    - **Pasos del Razonamiento (por cada API):**

      1.  **Agrupar y Promediar por Nivel:**
            - Agrupa los datos de `exactitud_metodo` por el campo `nivel`.
            - Para cada nivel, calcula el promedio de los valores de `recuperacion`.
            - Documenta los cálculos. Ejemplo: *Level I: valores [99.2, 100.3, 99.8] → promedio = 99.77%*.
      2.  **Comparar cada Nivel contra el Criterio:**
            - Extrae los límites numéricos del `criterio_exactitud` (ej: 98.0 y 102.0).
            - Compara el promedio de cada nivel contra este rango.
            - Documenta el resultado por nivel. Ejemplo: *Level I (99.77%): `98.0 ≤ 99.77 ≤ 102.0`. → Cumple.*
      3.  **Determinar Conclusión Global:**
            - Si **TODOS** los niveles cumplen el criterio → `conclusion_exactitud` es **"Cumple"**.
            - Si **AL MENOS UN** nivel no cumple → `conclusion_exactitud` es **"No Cumple"**.
      4.  **Justificación Final:** Redacta un resumen que explique la conclusión global, basado en los resultados de cada nivel.
      5.  Reporta si se cumple el criterio de exactitud del protocolo

  `</REGLAS_DE_RAZONAMIENTO>`

  <br>

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para la generación de la salida final.

    - **Modelo de Salida:** Un único objeto JSON bien formado que siga la estructura `Set4StructuredOutputSupervisor`. No incluyas texto fuera del JSON.

    - **Condición:** Genera la salida **solo después** de que el `reasoning_agent` haya completado y documentado su análisis.

    - **Integración de Datos:** La salida debe reflejar los **resultados promediados por nivel** que se calcularon en el razonamiento. La lista `exactitud_metodo` en la salida final contendrá una entrada por nivel con su promedio, no los datos crudos individuales.

    - **Ejemplo de Salida del Supervisor (Caso "Cumple"):**
      **OJO, EN EL EJEMPLO APENAS APARECE UNA RÉPLICA POR CADA NIVEL, PERO ESTO ES SÓLO A MODO DE EJEMPLO.. NECESITO QUE EXTRAIGAS TODA LA DATA, ES DECIR, TODAS LAS REPLICAS POR CADA NIVEL**
      ```json
      {
        "activos_exactitud": [
          {
            "nombre": "[api_1_nombre]",
            "exactitud_metodo": [
              { "nivel": "Level I", "recuperacion": 99.2, "recuperacion_promedio": 99.2" },
              { "nivel": "Level I", "recuperacion": 100.3, "recuperacion_promedio": 99.2 },
              { "nivel": "Level I", "recuperacion": 99.8, "recuperacion_promedio": 99.2 },
              { "nivel": "Level II", "recuperacion": 100.1, "recuperacion_promedio": 100.1 },
              { "nivel": "Level II", "recuperacion": 101.5, "recuperacion_promedio": 100.1 },
              { "nivel": "Level II", "recuperacion": 100.9, "recuperacion_promedio": 100.1 },
              { "nivel": "Level III", "recuperacion": 98.7, "recuperacion_promedio": 98.7 },
              { "nivel": "Level III", "recuperacion": 99.1, "recuperacion_promedio": 98.7 },
              { "nivel": "Level III", "recuperacion": 98.9, "recuperacion_promedio": 98.7 }
            ],
            "conclusion_exactitud": "Cumple",
            "criterio_exactitud": "El % de recuperación debe estar entre 98.0% y 102.0%"
          }
        ],
        "referencia_exactitud": "[lims_run_o_ref_analitica]"
      }
      ```
  `</REGLAS_DE_SALIDA_SUPERVISOR>`
"""

RULES_SET_5 = """
  `<REGLAS_DE_EXTRACCION_ESTRUCTURADA>`
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer los criterios de aceptación del protocolo de validación y los datos de ejecución EXACTOS CON CIFRAS SIGNIFICATIVAS IDENTICAS A LOS DOCUMENTOS de los reportes LIMS para evaluar la **precisión del sistema**, estructurando la información según el modelo `Set5ExtractionModel`.

  -----

    - **Fase 1: Extracción del Criterio de Aceptación desde el Protocolo**

        - **Fuente Primaria:** Documento VECTORSTORE .parque del **Protocolo de Validación**.
        - **Objetivo Específico:** Identificar y extraer únicamente el criterio de aceptación numérico para la precisión del sistema.
        - **Plan de Acción:**
          1.  **Enfócate en el protocolo.** Realiza búsquedas específicas en el documento del protocolo usando términos como "Precisión del sistema", "Criterio de aceptación", "RSD", "%RSD" o "Coeficiente de variación".
          2.  **Puebla el campo de criterio.** Asigna el texto extraído al campo `criterio_precision_sistema`.
        - **Salida de Fase 1 (Ejemplo):**
          ```json
          {
            "activos_precision_sistema": [
              {
                "nombre": "[api_1_nombre]",
                "criterio_precision_sistema": "El %RSD no debe ser mayor a 2.0%",
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de Datos de Ejecución desde el Reporte LIMS**

        - **Fuente Primaria:** Vectorstore .parquet del Reporte de datos crudos del **LIMS** o la **Hoja de Trabajo Analítica**.
        - **Objetivo Específico:** Extraer las réplicas de las inyecciones, el RSD% si fue pre-calculado por el software, y el identificador de la corrida.
        - **Plan de Acción:**
          1.  **Busca tablas de resultados.** Identifica tablas que contengan columnas como "N°", "Réplica", "Nombre", "Área" o "Valor" y "Unidad".
          2.  **Extrae datos crudos EXACTOS CON CIFRAS SIGNIFICATIVAS IDENTICAS.** Para cada API, extrae la lista de réplicas y sus áreas correspondientes.
          3.  **Extrae RSD% (si existe).** Busca explícitamente un valor etiquetado como "RSD%", "%RSD", o "Coef. Var. %" en la tabla de resumen de resultados. Si lo encuentras, asígnalo a `rsd_precision_sistema`.
          4.  **Extrae la referencia.** Identifica un código de corrida, ID de análisis o referencia única del reporte y asígnalo a `referencia_precision_sistema`.
        - **Normalización de Datos:**
            - `replica`: Mantener como texto original (ej: "1", "2", ...).
            - `area_activo`: Convertir a tipo flotante (`float`), unificando comas a puntos decimales.
            - Si falta algún dato en esta fase, déjalo como `null` o una lista vacía `[]`.

  -----

    - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
      ```json
      {
        "activos_precision_sistema": [
          {
            "nombre": "[api_1_nombre]",
            "precision_sistema": [
              { "replica": "1", "area_activo": <valor numérico exacto extraido de replica 1> },
              { "replica": "2", "area_activo": <valor numérico exacto extraido de replica 2> },
              { "replica": "3", "area_activo": <valor numérico exacto extraido de replica 3> },
              { "replica": "4", "area_activo": <valor numérico exacto extraido de replica 4> },
              { "replica": "5", "area_activo": <valor numérico exacto extraido de replica 5> },
              { "replica": "6", "area_activo": <valor numérico exacto extraido de replica 6> }
            ],
            "conclusion_precision_sistema": "[pendiente_validar]",
            "rsd_precision_sistema": 0.85, // Extraído del LIMS o null si no estaba
            "criterio_precision_sistema": "El %RSD no debe ser mayor a 2.0%"
          }
        ],
        "referencia_precision_sistema": "[lims_run_o_ref_analitica]"
      }
      ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  <br>

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Validar los datos extraídos, calcular el RSD% si es necesario, y comparar el resultado contra el criterio de aceptación para determinar si la precisión del sistema cumple con lo especificado.

    - **Entradas:** El objeto JSON poblado por el `structured_extraction_agent`.

    - **Pasos de Razonamiento (por cada API):**

      1.  **Verificar Datos de Entrada:** Confirma que la lista `precision_sistema` contiene datos numéricos válidos. Anota el número de réplicas encontradas.
      2.  **Comparar contra el Criterio:** Extrae el umbral numérico del texto `criterio_precision_sistema` (ej: 2.0). Compara el RSD% (extraído) contra este umbral.
      4.  **Determinar Conclusión:**
            - Si `RSD% ≤ Umbral_Criterio` → la conclusión es **"Cumple"**.
            - Si `RSD% > Umbral_Criterio` → la conclusión es **"No Cumple"**.
      5.  **Documentar Justificación:** Escribe una justificación clara y concisa. Ejemplo: *"Se encontraron 6 réplicas válidas. El RSD% calculado fue de 0.85%, que es menor o igual al criterio de aceptación de ≤ 2.0%. Por lo tanto, el sistema cumple."*
  `</REGLAS_DE_RAZONAMIENTO>`

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para generar la salida final.

    - **Modelo de Salida:** `Set5StructuredOutputSupervisor` en formato **JSON estrictamente**. No debe haber ningún texto fuera del objeto JSON.

    - **Condición:** La salida solo se debe emitir **después** de que el `reasoning_agent` haya completado y documentado su análisis.

    - **Integración de Datos:**

        - Copia la lista `precision_sistema` con las réplicas válidas.
        - Utiliza el valor final de `rsd_precision_sistema` (ya sea el extraído o el calculado).
        - Actualiza el campo `conclusion_precision_sistema` con el resultado del razonamiento ("Cumple" o "No Cumple").
        - Incluye el `criterio_precision_sistema` para total trazabilidad.
        - Asegúrate de que `referencia_precision_sistema` esté presente en la raíz del objeto.

    - **Ejemplo de Salida Final del Supervisor (Caso "Cumple"):**

      ```json
      {
        "activos_precision_sistema": [
          {
            "nombre": "[api_1_nombre]",
            "precision_sistema": [
              { "replica": "1", "area_activo": <valor numérico exacto extraido de replica 1> },
              { "replica": "2", "area_activo": <valor numérico exacto extraido de replica 2> },
              { "replica": "3", "area_activo": <valor numérico exacto extraido de replica 3> },
              { "replica": "4", "area_activo": <valor numérico exacto extraido de replica 4> },
              { "replica": "5", "area_activo": <valor numérico exacto extraido de replica 5> },
              { "replica": "6", "area_activo": <valor numérico exacto extraido de replica 6> }
            ],
            "conclusion_precision_sistema": "Cumple",
            "criterio_precision_sistema": "El %RSD no debe ser mayor a 2.0%",
            "rsd_precision_sistema": 0.85
          }
        ],
        "referencia_precision_sistema": "[lims_run_o_ref_analitica]"
      }
      ```
"""

RULES_SET_6 = """
  `<REGLAS_DE_EXTRACCION_ESTRUCTURADA>`
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer el criterio de aceptación para la **precisión del método** desde el protocolo de validación y los datos experimentales (valoraciones individuales) desde los reportes LIMS, estructurando la información según el modelo `Set6ExtractionModel`.

  -----

    - **Fase 1: Extracción del Criterio de Aceptación desde el Protocolo**

        - **Fuente Primaria:** Documento del **Protocolo de Validación**.
        - **Objetivo Específico:** Identificar y extraer el criterio de aceptación para la Desviación Estándar Relativa (RSD).
        - **Plan de Acción:**
          1.  **Enfócate en el protocolo.** Realiza búsquedas específicas usando términos como "Precisión del método", "Repetibilidad", "Method Precision", "Criterio de Aceptación", y "%RSD".
          2.  **Busca el umbral de RSD%.** El criterio se expresa típicamente como un límite máximo. Por ejemplo: "El %RSD de las seis preparaciones no debe ser mayor a 2.0%". Extrae este texto.
          3.  **Puebla el campo de criterio.** Asigna el texto extraído al campo `criterio_precision_metodo`.
        - **Salida de Fase 1 (Ejemplo):**
          ```json
          {
            "activos_precision_metodo": [
              {
                "nombre": "[api_1_nombre]",
                "criterio_precision_metodo": "El %RSD no debe ser mayor a 2.0%",
                "precision_metodo": [],
                "rsd_precision_metodo": null,
                "conclusion_precision_metodo": "[pendiente_datos]"
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de Datos de Ejecución desde el Reporte LIMS**

        - **Fuente Primaria:** Reporte de datos crudos del **LIMS** o la **Hoja de Trabajo Analítica**.
        - **Objetivo Específico:** Extraer la lista completa de valoraciones (% de activo) para todas las réplicas y el RSD% si el software ya lo ha calculado.
        - **Plan de Acción:**
          1.  **Busca la tabla de resultados.** Identifica la tabla correspondiente a "Precisión del Método" o "Repetibilidad". Debe contener columnas como "Réplica", "Muestra N°" y "Valoración %" o "Resultado".
          2.  **Extrae todas las réplicas.** Captura cada resultado individual en la lista `precision_metodo`. Es crucial no omitir ninguna réplica.
          3.  **Busca el RSD% pre-calculado.** Revisa si al final de la tabla o en una sección de resumen, el reporte ya incluye un valor para "RSD%" o "% C.V.". Si existe, extráelo y asígnalo a `rsd_precision_metodo`. Si no, déjalo como `null`.
          4.  **Extrae la referencia.** Localiza el identificador del análisis (ej. "RUN-...") y asígnalo a `referencia_precision_metodo`.
        - **Normalización de Datos:**
            - `replica`: Mantener como texto original.
            - `porcentaje_activo`: Convertir a tipo flotante (`float`), unificando comas a puntos decimales.

  -----

    - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
      ```json
      {
        "activos_precision_metodo": [
          {
            "nombre": "[nombre_ingrediente_activo]",
            "precision_metodo": [
              { "replica": "1", "porcentaje_activo": 99.8 },
              { "replica": "2", "porcentaje_activo": 100.3 },
              { "replica": "3", "porcentaje_activo": 100.1 },
              { "replica": "4", "porcentaje_activo": 99.7 },
              { "replica": "5", "porcentaje_activo": 100.0 },
              { "replica": "6", "porcentaje_activo": 99.9 }
            ],
            "conclusion_precision_metodo": "[pendiente_validar]",
            "rsd_precision_metodo": null, // El LIMS no lo reportó, se calculará después
            "criterio_precision_metodo": "El %RSD no debe ser mayor a 2.0%"
          }
        ],
        "referencia_precision_metodo": "[lims_run_o_ref_analitica]"
      }
      ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  <br>

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Validar los datos, calcular el RSD% (si es necesario) y compararlo contra el criterio de aceptación para determinar si el método es preciso.

    - **Entradas:** El objeto JSON completo del `structured_extraction_agent`.

    - **Pasos del Razonamiento (por cada API):**

      1.  **Verificar Datos de Entrada:** Confirma que la lista `precision_metodo` contiene datos válidos. Anota el número de réplicas (`N`).
      2.  **Calcular RSD% (si es necesario):**
            - **SI** el campo `rsd_precision_metodo` es `null`:
                - Calcula el promedio de `porcentaje_activo`.
                - Calcula la desviación estándar (σ, n-1) de `porcentaje_activo`.
                - Calcula el RSD% con la fórmula: `RSD% = (desviación_estándar / promedio) * 100`.
                - Documenta los cálculos intermedios (N, promedio, desv. est.) y el resultado.
            - **SI** `rsd_precision_metodo` ya fue extraído, úsalo directamente, anotando que es el valor reportado por el LIMS.
      3.  **Comparar con Criterio:** Extrae el umbral numérico del `criterio_precision_metodo` (ej: 2.0). Compara el RSD% final contra este umbral.
      4.  **Determinar Conclusión:**
            - Si `RSD% ≤ Umbral_Criterio` → la conclusión es **"Cumple"**.
            - Si `RSD% > Umbral_Criterio` → la conclusión es **"No Cumple"**.
      5.  **Justificación Final:** Escribe un resumen conciso. Ejemplo: *"Se analizaron N=6 réplicas. El RSD% calculado fue de 0.22%, el cual es menor o igual al criterio de aceptación de ≤ 2.0%. Por lo tanto, el método cumple."*

  `</REGLAS_DE_RAZONAMIENTO>`

  <br>

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para generar la salida final.

    - **Modelo de Salida:** Un único objeto JSON bien formado que siga la estructura `Set6StructuredOutputSupervisor`. No incluyas texto fuera del JSON.

    - **Condición:** Genera la salida **solo después** de que el `reasoning_agent` haya completado y documentado su análisis.

    - **Integración de Datos:** El JSON final debe contener los datos crudos (`precision_metodo`), el `criterio_precision_metodo`, el RSD% final (calculado o extraído), y la `conclusion_precision_metodo` determinada por el razonamiento.

    - **Ejemplo de Salida del Supervisor (Caso "Cumple"):**

      ```json
      {
        "activos_precision_metodo": [
          {
            "nombre": "[nombre_ingrediente_activo]",
            "precision_metodo": [
              { "replica": "1", "porcentaje_activo": 99.8 },
              { "replica": "2", "porcentaje_activo": 100.3 },
              { "replica": "3", "porcentaje_activo": 100.1 },
              { "replica": "4", "porcentaje_activo": 99.7 },
              { "replica": "5", "porcentaje_activo": 100.0 },
              { "replica": "6", "porcentaje_activo": 99.9 }
            ],
            "conclusion_precision_metodo": "Cumple",
            "rsd_precision_metodo": 0.22,
            "criterio_precision_metodo": "El %RSD no debe ser mayor a 2.0%"
          }
        ],
        "referencia_precision_metodo": "[lims_run_o_ref_analitica]"
      }
      ```

  `</REGLAS_DE_SALIDA_SUPERVISOR>`
"""

RULES_SET_7 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al structured_extraction_agent.

  - Objetivo: Extraer información de PRECISIÓN INTERMEDIA por API desde reportes LIMS (dos analistas) y protocolo (criterios) y estructurarla según Set7ExtractionModel (lista de ActivoPrecisionIntermediaStrExt).

  - Plan iterativo (varios ciclos sobre el vectorstore):
    1) Descubrimiento de APIs con precisión intermedia: localizar tablas con réplicas tipo "Solucion Muestra 1..6" y columnas A1D1E1 (analista 1) y A2D2E2 (analista 2).
    2) Extracción por API (subciclo por API):
      • precision_intermedia → lista de {replica, porcentaje_an1, porcentaje_an2} desde LIMS.  
      • rsd_an1_an2 → tomar del LIMS si aparece como RSD%; si falta, marcar "[pendiente_validar]".  
      • diferencia_promedio_an1_an2 → tomar del LIMS si existe; si no, "[pendiente_validar]".  
      • criterio_precision_intermedia → extraer del Protocolo (tabla de criterios; incluir umbrales de RSD% y diferencia de promedios si aplican).
      • conclusion → "[pendiente_validar]".
    3) Trazabilidad obligatoria (ledger interno, no en la salida): source_document (LIMS/Protocolo), page_or_span, query_used, confidence, cleaning_notes.
    4) Normalización mínima:
      • Unificar decimales coma→punto; límites 0–200.  
      • Mantener literal de las réplicas y nombres tal como figuran.  
    5) Deduplificación: si hay varias corridas, unificar por (api, replica, run_id) conservando la más completa/reciente; registrar motivo.
    6) Relleno de huecos: si persisten faltantes tras los ciclos, usar "[pendiente_validar]" y documentar causa en trazabilidad.

  - Ejemplo de extracción estructurada (Set7ExtractionModel):
  {
    "activos_precision_intermedia": [
      {
        "nombre": "[api_1_nombre]",
        "precision_intermedia": [
          { "replica": "Solucion Muestra 1", "porcentaje_an1": 100.2, "porcentaje_an2": 99.8 },
          { "replica": "Solucion Muestra 2", "porcentaje_an1": 100.1, "porcentaje_an2": 100.0 },
          { "replica": "Solucion Muestra 3", "porcentaje_an1": 99.9,  "porcentaje_an2": 100.3 },
          { "replica": "Solucion Muestra 4", "porcentaje_an1": 100.4, "porcentaje_an2": 100.1 },
          { "replica": "Solucion Muestra 5", "porcentaje_an1": 99.7,  "porcentaje_an2": 99.9 },
          { "replica": "Solucion Muestra 6", "porcentaje_an1": 100.0, "porcentaje_an2": 100.2 }
        ],
        "conclusion": "[pendiente_validar]",
        "rsd_an1_an2": "[pendiente_validar]",
        "diferencia_promedio_an1_an2": "[pendiente_validar]",
        "criterio_precision_intermedia": [
          {
            "criterio_selectividad": "[na]",
            "criterio_linealidad": "[na]",
            "criterio_exactitud": "[na]",
            "criterio_precision_sistema": "[na]",
            "criterio_precision_metodo": "[na]",
            "criterio_precision_intermedia": "[umbral_rsd: <= 2.0% ; umbral_diferencia_promedios: <= 2.0%]",
            "criterio_rango": "[na]",
            "criterio_estabilidad_soluciones": "[na]",
            "criterio_estabilidad_fase_movil": "[na]",
            "criterio_robustez": "[na]"
          }
        ]
      }
    ]
  }
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al reasoning_agent.

  - RESTRICCIÓN CLAVE: El razonamiento SIEMPRE debe preceder a cualquier verificación, clasificación o salida final. Documentar pasos e inferencias.

  - Pasos mínimos por API (documentar explícitamente):
    1) Cálculo de promedios por analista:
      • promedio_an1 = mean(porcentaje_an1 de todas las réplicas válidas)  
      • promedio_an2 = mean(porcentaje_an2 de todas las réplicas válidas)
    2) Diferencia de promedios:
      • diferencia_promedio_an1_an2 = abs(promedio_an1 - promedio_an2)
    3) RSD combinado:
      • Si LIMS reporta rsd_an1_an2 → usarlo.  
      • Si no, calcular RSD% sobre el conjunto combinado de valores de ambos analistas:  
        promedio_conjunto = mean(valores_an1 ∪ valores_an2)  
        desv_est = std(valores_an1 ∪ valores_an2, n-1)  
        rsd_an1_an2 = 100 * (desv_est / promedio_conjunto)  
        Documentar valores usados (promedios y desviación).
      • Nota: si el criterio exige RSD por analista, calcular también rsd_an1 y rsd_an2 y registrar ambos antes de concluir.
    4) Comparación con criterios del Protocolo:
      • Regla típica: rsd_an1_an2 <= [umbral_rsd] Y diferencia_promedio_an1_an2 <= [umbral_diferencia].  
      • Si cualquiera falla → "No Cumple".
    5) Conclusión global:
      • conclusion = "Cumple" | "No Cumple"  
      • Justificación breve con números y umbrales aplicados.

  - Ejemplo de razonamiento (orden correcto):
    • promedio_an1 = 100.05 ; promedio_an2 = 100.05 → diferencia = 0.00%  
    • Conjunto 12 valores → promedio_conjunto = 100.03 ; desv_est = 0.65 → RSD% = 0.65%  
    • Criterios: RSD% <= 2.0% y diferencia <= 2.0% → Cumple  
    • Conclusión API [api_1_nombre] = "Cumple".
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  Estas reglas aplican al supervisor.

  - Modelo de salida: Set7StructuredOutputSupervisor en JSON bien formado. Solo el JSON final (sin texto extra).
  - Condición: emitir salida únicamente después de que el razonamiento esté documentado.
  - Integración:
    • Transformar a ActivoPrecisionIntermediaStrOutput.  
    • Incluir en cada réplica un campo promedio_analistas con un único elemento {promedio_an1, promedio_an2} (repetido por réplica para cumplir el modelo).  
    • Completar rsd_an1_an2, diferencia_promedio_an1_an2 y conclusion.  
    • Añadir referencia_precision_intermedia.

  - Ejemplo de salida del supervisor (orden: 1) razonamiento → 2) salida):
  Razonamiento (resumen): promedio_an1=100.05 ; promedio_an2=100.05 ; diferencia=0.00 ; RSD%=0.65 ; umbrales 2.0%/2.0% → Cumple.

  {
    "activos_precision_intermedia": [
      {
        "nombre": "[api_1_nombre]",
        "precision_intermedia": [
          {
            "replica": "Solucion Muestra 1",
            "porcentaje_an1": 100.2,
            "porcentaje_an2": 99.8,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          },
          {
            "replica": "Solucion Muestra 2",
            "porcentaje_an1": 100.1,
            "porcentaje_an2": 100.0,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          },
          {
            "replica": "Solucion Muestra 3",
            "porcentaje_an1": 99.9,
            "porcentaje_an2": 100.3,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          },
          {
            "replica": "Solucion Muestra 4",
            "porcentaje_an1": 100.4,
            "porcentaje_an2": 100.1,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          },
          {
            "replica": "Solucion Muestra 5",
            "porcentaje_an1": 99.7,
            "porcentaje_an2": 99.9,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          },
          {
            "replica": "Solucion Muestra 6",
            "porcentaje_an1": 100.0,
            "porcentaje_an2": 100.2,
            "promedio_analistas": [ { "promedio_an1": 100.05, "promedio_an2": 100.05 } ]
          }
        ],
        "conclusion": "Cumple",
        "rsd_an1_an2": 0.65,
        "diferencia_promedio_an1_an2": 0.00,
        "criterio_precision_intermedia": [
          {
            "criterio_selectividad": "[na]",
            "criterio_linealidad": "[na]",
            "criterio_exactitud": "[na]",
            "criterio_precision_sistema": "[na]",
            "criterio_precision_metodo": "[na]",
            "criterio_precision_intermedia": "[umbral_rsd: <= 2.0% ; umbral_diferencia_promedios: <= 2.0%]",
            "criterio_rango": "[na]",
            "criterio_estabilidad_soluciones": "[na]",
            "criterio_estabilidad_fase_movil": "[na]",
            "criterio_robustez": "[na]"
          }
        ]
      }
    ],
    "referencia_precision_intermedia": "[lims_run_o_ref_analitica]"
  }

  — RESTRICCIÓN CRÍTICA (repetir siempre): RAZONAMIENTO → LUEGO SALIDA. Cualquier cálculo o inferencia debe documentarse antes de la salida final.
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
"""

RULES_SET_8 = """


"""

RULES_SET_9 = """


"""

RULES_SET_10 = """


"""

RULES_SET_11 = """


"""
