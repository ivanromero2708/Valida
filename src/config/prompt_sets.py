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
        - **Objetivo Específico:** Extraer la curva de calibración completa (todos los niveles con **todas sus réplicas**) y los parámetros de regresión calculados por el software **PARA CADA ACTIVO INDIVIDUAL**.
        - **CRÍTICO - PROCESAMIENTO MULTI-ACTIVO:** 
          - **DEBES procesar TODOS los vectorstores de reportes LIMS disponibles en la lista de documentos**
          - **DEBES extraer datos para CADA activo encontrado en CADA vectorstore por separado**
          - **DEBES consolidar TODOS los activos en una sola lista `activos_linealidad`**
          - **DEBES incluir TODAS las referencias en la lista `referencia_linealidad`**
        - **Plan de Acción:**
          1.  **Procesa CADA vectorstore de reporte LIMS individualmente.** Para cada vectorstore que contenga "REPORTE_LINEALIDAD" en su nombre:
             a. **Identifica el activo del reporte.** Busca en el título del documento términos como "VALORACIÓN", "LINEARITY RESULTS" seguidos del nombre del activo.
             b. **Extrae el nombre del activo.** Captura el nombre exacto del ingrediente activo desde el título o encabezado del reporte.
          2.  **Para CADA activo identificado:**
             a. **Extrae la curva de calibración completa.** Busca la tabla principal de datos de linealidad. Debe contener columnas como "Level", "Concentration", "Response", y "Response Factor". **Es crucial que extraigas una entrada por cada inyección/réplica individual**, no un promedio por nivel.
             b. **Extrae los parámetros de regresión.** Busca en las secciones de estadísticas los valores numéricos para `Slope` (pendiente), `Intercept` (intercepto), `Correlation Coefficient (r)`, `Determination Coefficient (r2)`.
             c. **Extrae los cálculos de resumen.** Busca valores como `RSD Response Factor` y `Intercept as percentage of Y at 100%`.
             d. **Extrae la referencia específica.** Identifica el código de referencia único del reporte (ej. "HT001/25-XXXXX ID-VAL").
          3.  **Consolida en estructura final.** Crea un elemento en `activos_linealidad` por cada activo procesado y agrega todas las referencias a `referencia_linealidad`.
        
        - **VALIDACIÓN OBLIGATORIA:**
          - **Verifica que el número de elementos en `activos_linealidad` coincida con el número de vectorstores de reportes LIMS procesados**
          - **Si falta algún activo, revisa los vectorstores nuevamente con búsquedas más amplias**

    - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
      *NOTA: Este ejemplo muestra múltiples activos genéricos con múltiples réplicas por nivel. DEBES extraer TODOS los activos encontrados en los vectorstores.*

      ```json
      {
        "activos_linealidad": [
          {
            "nombre": "[NOMBRE_ACTIVO_1_EXTRAIDO_DEL_REPORTE]",
            "linealidad_sistema": [
              { "nivel": "[NIVEL_EXTRAIDO]", "replica": 1, "concentracion": [VALOR_EXTRAIDO], "area_pico": [VALOR_EXTRAIDO] },
              { "nivel": "[NIVEL_EXTRAIDO]", "replica": 2, "concentracion": [VALOR_EXTRAIDO], "area_pico": [VALOR_EXTRAIDO] },
              { "nivel": "[NIVEL_EXTRAIDO]", "replica": 3, "concentracion": [VALOR_EXTRAIDO], "area_pico": [VALOR_EXTRAIDO] }
              // ... TODAS las réplicas de TODOS los niveles
            ],
            "rsd_factor": [VALOR_EXTRAIDO_RSD],
            "pendiente": [VALOR_EXTRAIDO_SLOPE],
            "intercepto": [VALOR_EXTRAIDO_INTERCEPT],
            "r": [VALOR_EXTRAIDO_CORRELATION],
            "r2": [VALOR_EXTRAIDO_DETERMINATION],
            "porcentaje_intercepto": [VALOR_EXTRAIDO_PERCENTAGE],
            "criterio_linealidad": "[CRITERIO_EXTRAIDO_DEL_PROTOCOLO]"
          },
          {
            "nombre": "[NOMBRE_ACTIVO_2_EXTRAIDO_DEL_REPORTE]",
            "linealidad_sistema": [
              { "nivel": "[NIVEL_EXTRAIDO]", "replica": 1, "concentracion": [VALOR_EXTRAIDO], "area_pico": [VALOR_EXTRAIDO] },
              { "nivel": "[NIVEL_EXTRAIDO]", "replica": 2, "concentracion": [VALOR_EXTRAIDO], "area_pico": [VALOR_EXTRAIDO] }
              // ... TODAS las réplicas de TODOS los niveles para este activo
            ],
            "rsd_factor": [VALOR_EXTRAIDO_RSD],
            "pendiente": [VALOR_EXTRAIDO_SLOPE],
            "intercepto": [VALOR_EXTRAIDO_INTERCEPT],
            "r": [VALOR_EXTRAIDO_CORRELATION],
            "r2": [VALOR_EXTRAIDO_DETERMINATION],
            "porcentaje_intercepto": [VALOR_EXTRAIDO_PERCENTAGE],
            "criterio_linealidad": "[CRITERIO_EXTRAIDO_DEL_PROTOCOLO]"
          }
          // ... TANTOS ELEMENTOS COMO ACTIVOS ENCUENTRES EN LOS VECTORSTORES
        ],
        "referencia_linealidad": ["[REFERENCIA_ACTIVO_1]", "[REFERENCIA_ACTIVO_2]", "[REFERENCIA_ACTIVO_N]"]
      }
      ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  <br>

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Comparar sistemáticamente cada parámetro de regresión extraído contra su criterio de aceptación correspondiente para emitir una conclusión global sobre la linealidad del método, y generar las gráficas de regresión y residuales correspondientes.

    - **Entradas:** El objeto JSON completo poblado por el `structured_extraction_agent`.

    - **Pasos del Razonamiento:**

      1.  **Generar Gráficas de Linealidad:** ANTES de realizar cualquier comparación, usa la herramienta `linealidad_tool` para generar las gráficas de regresión y residuales:
            - Extrae los datos de `linealidad_sistema` de cada activo
            - Para cada activo, llama a `linealidad_tool` con los parámetros:
              - `nombre_activo`: nombre del API
              - `datos_linealidad`: lista de puntos con concentracion y area_pico
              - `criterios_aceptacion`: criterios extraídos del protocolo
            - **IMPORTANTE:** La herramienta generará automáticamente las gráficas y retornará las rutas absolutas en `regresion_png_path` y `residuales_png_path`
            - Documenta las rutas generadas para cada activo

      2.  **Iterar por Criterio:** Para cada parámetro en la lista `criterio_linealidad`, busca el valor experimental correspondiente (ej: si `parametro` es "Coeficiente de correlación (r)", busca el valor de `r`).

      3.  **Documentar Comparación:** Realiza y documenta la comparación numérica de forma explícita.
            - **Ejemplo 1:** *Verificación (r): Valor obtenido `r = 0.9999`. Criterio `≥ 0.995`. Comparación: `0.9999 ≥ 0.995` es VERDADERO. → Cumple.*
            - **Ejemplo 2:** *Verificación (RSD): Valor obtenido `rsd_factor = 1.5%`. Criterio `≤ 2.0%`. Comparación: `1.5 ≤ 2.0` es VERDADERO. → Cumple.*

      4.  **Conclusión Global:** Emite una conclusión para `cumple_global`.
            - Si **TODOS** los parámetros individuales cumplen su criterio → **"Cumple"**.
            - Si **AL MENOS UNO** de los parámetros no cumple su criterio → **"No Cumple"**.

      5.  **Justificación Final:** Proporciona un resumen que justifique la conclusión global, mencionando qué parámetros cumplieron o no.

      6.  **Entregar Rutas de Gráficas al Supervisor:** Asegúrate de documentar y entregar al supervisor las rutas de las gráficas generadas:
            - `regresion_png_path`: ruta absoluta de la gráfica de regresión
            - `residuales_png_path`: ruta absoluta de la gráfica de residuales
            - Estas rutas deben incluirse en la salida estructurada final

  `</REGLAS_DE_RAZONAMIENTO>`

  <br>

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para generar la salida final.

    - **Modelo de Salida:** Un único objeto JSON que se adhiere estrictamente al modelo `Set3StructuredOutputSupervisor`. No incluyas texto o explicaciones fuera del JSON.

    - **Condición:** Genera la salida **solo después** de que el `reasoning_agent` haya documentado su análisis completo.

    - **Integración de Datos:** El JSON final debe contener los datos experimentales (`linealidad_sistema`, `r`, `pendiente`, etc.), los criterios (`criterio_linealidad`), la conclusión final validada (`cumple_global`) y **OBLIGATORIAMENTE** las rutas de las gráficas generadas (`regresion_png_path`, `residuales_png_path`).

    - **IMPORTANTE:** El supervisor debe incluir las rutas de las gráficas que fueron generadas por el `reasoning_agent` usando la herramienta `linealidad_tool`.

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
            "criterio_linealidad": "Coeficiente de correlación (r) criterio": "≥ 0.995",
            "regresion_png_path": "RUTA A LA IMAGEN DE GRAFICO DE REGRESION",
            "residuales_png_path": "RUTA A LA IMAGEN DE GRAFICO DE RESIDUALES"
          }
        ],
        "referencia_linealidad": ["[HT001XXXXXX]"],        
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

    - **Objetivo General:** Extraer los criterios de aceptación para la **precisión intermedia** desde el protocolo de validación y los dos conjuntos de datos experimentales desde los reportes LIMS, estructurando la información según el modelo `Set7ExtractionModel`.

  -----

    - **Fase 1: Extracción de Criterios de Aceptación desde el Protocolo**

        - **Fuente Primaria:** Documento del **Protocolo de Validación**.
        - **Objetivo Específico:** Identificar y extraer los criterios de aceptación para la precisión intermedia. Estos suelen incluir un criterio para el RSD global y un criterio para la comparación de medias (prueba t).
        - **Plan de Acción:**
          1.  **Enfócate en el protocolo.** Realiza búsquedas específicas usando términos como "Precisión intermedia", "Intermediate Precision", "Comparación de medias", "Prueba t de Student", "RSD global".
          2.  **Busca los criterios.** Localiza el texto que define los límites aceptables. Por ejemplo: "El RSD global de las 12 determinaciones debe ser ≤ 3.0%" y "Las medias de los dos conjuntos de datos no deben ser estadísticamente diferentes (prueba t, α=0.05)".
          3.  **Puebla el campo de criterio.** Extrae y asigna estos textos al campo `criterio_precision_intermedia`.
        - **Salida de Fase 1 (Ejemplo):**
          ```json
          {
            "activos_precision_intermedia": [
              {
                "nombre": "[nombre_ingrediente_activo]",
                "criterio_precision_intermedia": "RSD global de 12 réplicas ≤ 3.0%; Las medias no deben ser estadísticamente diferentes (t-test, 95% confianza)."
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de los Dos Conjuntos de Datos desde Reportes LIMS**

        - **Fuente Primaria:** Dos reportes de datos crudos del **LIMS** o Hojas de Trabajo Analíticas, cada uno representando un conjunto de condiciones (ej. Analista 1/Día 1 y Analista 2/Día 2).
        - **Objetivo Específico:** Extraer los dos conjuntos completos de valoraciones (% de activo) que conforman el estudio de precisión intermedia.
        - **CRÍTICO - Procesamiento de Múltiples Reportes:**
            - **DEBES** identificar y procesar los dos reportes LIMS que contienen los datos para la comparación.
            - **DEBES** asignar los datos de un reporte al `conjunto_1` y los del otro al `conjunto_2`.
            - **DEBES** capturar las referencias de ambos reportes.
        - **Plan de Acción:**
          1.  **Identifica los dos reportes.** Busca reportes de precisión que se diferencien por una variable clave (analista, fecha, equipo, etc.).
          2.  **Procesa el Primer Reporte.** Extrae la tabla de resultados (columnas "Réplica", "Resultado %") y asigna la lista completa de datos a `conjunto_1`. Extrae su ID de referencia.
          3.  **Procesa el Segundo Reporte.** Extrae la tabla de resultados de la misma manera y asigna la lista completa de datos a `conjunto_2`. Extrae su ID de referencia.
        - **Ejemplo de Extracción Completa (Pre-Razonamiento):**
          ```json
          {
            "activos_precision_intermedia": [
              {
                "nombre": "[nombre_ingrediente_activo_1]",
                "precision_metodo": [
                  { "replica": "1", "porcentaje_activo": 99.8 },
                  { "replica": "2", "porcentaje_activo": 100.3 },
                  { "replica": "3", "porcentaje_activo": 100.1 },
                  { "replica": "4", "porcentaje_activo": 99.7 },
                  { "replica": "5", "porcentaje_activo": 100.0 },
                  { "replica": "6", "porcentaje_activo": 99.9 }
                ],                
                "criterio_precision_intermedia": "RSD global de 12 réplicas ≤ 3.0%; Las medias no deben ser estadísticamente diferentes (t-test, 95% confianza)."
              },{
                "nombre": "[nombre_ingrediente_activo_2]",
                "precision_metodo": [
                  { "replica": "1", "porcentaje_activo": 100.5 },
                  { "replica": "2", "porcentaje_activo": 100.8 },
                  { "replica": "3", "porcentaje_activo": 99.9 },
                  { "replica": "4", "porcentaje_activo": 101.0 },
                  { "replica": "5", "porcentaje_activo": 100.2 },
                  { "replica": "6", "porcentaje_activo": 100.7 }
                ],
                "criterio_precision_intermedia": "RSD global de 12 réplicas ≤ 3.0%; Las medias no deben ser estadísticamente diferentes (t-test, 95% confianza)."
              }
            ],
            "referencia_precision_intermedia": "[ref_conjunto_1]", "[ref_conjunto_2]"
          }
          ```

  `</REGLAS_DE_EXTRACCION_ESTRUCTURADA>`

  <br>

  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`. **NO utilizarás `linealidad_tool` ni ninguna otra herramienta de graficado.**

    - **Objetivo Principal:** Realizar un análisis estadístico para comparar las medias de los dos conjuntos de datos (Prueba t de Student) y evaluar el RSD global contra los criterios del protocolo.

    - **Entradas:** El objeto JSON completo del `structured_extraction_agent`.

    - **Pasos del Razonamiento (por cada API):**

      1.  **Cálculos Estadísticos por Conjunto:**
            - Para `conjunto_1`: Documenta N₁, promedio₁, desv. est₁ y RSD₁%.
            - Para `conjunto_2`: Documenta N₂, promedio₂, desv. est₂ y RSD₂%.
      2.  **Cálculos Estadísticos Globales:**
            - Combina todos los datos de `conjunto_1` y `conjunto_2`.
            - Documenta N\_total, y el RSD\_global%.
      3.  **Ejecutar Prueba t de Student para Comparar Medias:**
            - **Hipótesis Nula (H₀):** Las medias de los dos conjuntos son iguales (μ₁ = μ₂).
            - **Cálculos Intermedios (Documentar cada paso):**
                - Varianza ponderada (`Sp²`): `Sp² = [((N₁-1)*s₁²) + ((N₂-1)*s₂²)] / (N₁ + N₂ - 2)`
                - Desviación estándar ponderada (`Sp`): `Sp = sqrt(Sp²)`
                - Valor t calculado (`t_calculado`): `t_calculado = |promedio₁ - promedio₂| / (Sp * sqrt(1/N₁ + 1/N₂))`
            - **Obtener Valor t Crítico (`t_critico`):**
                - Grados de libertad (`gl`): `gl = N₁ + N₂ - 2`.
                - Nivel de significancia (`α`): 0.05 (para 95% de confianza).
                - Busca el valor `t_critico` de dos colas en una tabla t de Student para los `gl` y `α` calculados.
      4.  **Evaluar Criterios y Concluir:**
            - **Evaluación de Medias:** Compara `t_calculado` vs `t_critico`. Si `t_calculado ≤ t_critico`, las medias **NO son** estadísticamente diferentes. → **Cumple**.
            - **Evaluación de Precisión Global:** Compara `RSD_global%` vs el criterio del protocolo (ej. ≤ 3.0%). → **Cumple/No Cumple**.
            - **Conclusión Final (`conclusion_precision_intermedia`):** El resultado es **"Cumple"** solo si **ambas** evaluaciones (medias y RSD global) cumplen. Si una falla, el resultado es **"No Cumple"**.
      5.  **Justificación Final:** Escribe un resumen claro. Ejemplo: *"La prueba t de Student (t\_calc=X.XX ≤ t\_crit=Y.YY) demuestra que las medias no son estadísticamente diferentes. El RSD global (Z.ZZ%) cumple con el criterio de ≤ 3.0%. Por lo tanto, el método cumple con la precisión intermedia."*

  `</REGLAS_DE_RAZONAMIENTO>`

  <br>

  `<REGLAS_DE_SALIDA_SUPERVISOR>`
  Estas reglas aplican al `supervisor` para generar la salida final.

    - **Modelo de Salida:** Un único objeto JSON bien formado que siga la estructura `Set7StructuredOutputSupervisor`.

    - **Condición:** Generar la salida solo después de que el `reasoning_agent` haya documentado su análisis estadístico completo.

    - **Integración de Datos:** El JSON final debe incluir los datos crudos, los resultados del análisis estadístico (`comparacion_conjuntos`), la conclusión final y los criterios.

    - **Ejemplo de Salida del Supervisor (Caso "Cumple"):**

      ```json
      {
        "activos_precision_intermedia": [
          {
            "nombre": "[nombre_ingrediente_activo]",
            "conjunto_1": [
              { "replica": "1", "porcentaje_activo": 99.8 } // ... y las demás réplicas
            ],
            "conjunto_2": [
              { "replica": "1", "porcentaje_activo": 100.5 } // ... y las demás réplicas
            ],
            "comparacion_conjuntos": {
              "rsd_global": 0.45,
              "t_calculado": 1.85,
              "t_critico": 2.228,
              "conclusion_medias": "Estadísticamente Iguales"
            },
            "conclusion_precision_intermedia": "Cumple",
            "criterio_precision_intermedia": "RSD global de 12 réplicas ≤ 3.0%; Las medias no deben ser estadísticamente diferentes (t-test, 95% confianza)."
          }
        ],
        "referencia_precision_intermedia": ["[ref_conjunto_1]", "[ref_conjunto_2]"]
      }
      ```

  `</REGLAS_DE_SALIDA_SUPERVISOR>`
"""

RULES_SET_7 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer y estructurar la informacion de **precision intermedia** por ingrediente activo (API) en dos fases diferenciadas, siguiendo el modelo `Set7ExtractionModel`.

  -----

    - **Fase 1: Extraccion de criterios del protocolo de validacion**

        - **Fuente primaria:** Vectorstore .parquet del **Protocolo de Validacion** disponible en vectorstore.
        - **Objetivo especifico:** Identificar para cada API los limites de aceptacion y condiciones aplicables al estudio de precision intermedia (numero de analistas, replicas, umbrales de %RSD y diferencias entre promedios).
        - **Plan de accion:**
          1.  Localiza tablas o listas bajo los titulos "Precision intermedia", "Intermediate precision" o "Ruggedness".
          2.  Extrae literalmente los criterios numericos y condiciones asociadas (ej.: `%RSD <= 2.0%`, `|diferencia promedio| <= 2.0%`, "dos analistas", "seis replicas").
          3.  Si alguna consulta devuelve "Vectorstore is empty" o la ruta del parquet no coincide con `<LISTA_DOCS>` (por ejemplo, falta "- Grupo Procaps"), corrige la ruta antes de concluir que el criterio no existe y reintenta la busqueda.
          4.  No utilices marcadores de posicion (`[pendiente...]`, `No disponible`) en `criterio_precision_intermedia`; si tras reintentos documentados no hay informacion, registra el problema en `issues` y no emitas ese API.
        - **Salida esperada Fase 1 (ejemplo sintetico):**
          ```json
          {
            "activos_precision_intermedia": [
              {
                "nombre": "[API_PRINCIPAL]",
                "criterio_precision_intermedia": "Aceptar si %RSD <= 2.0% y |diferencia promedio| <= 2.0% (dos analistas, seis replicas)."
              }
            ]
          }
          ```

  -----

    - **Fase 2: Extraccion de datos experimentales (hojas de trabajo / LIMS)**

        - **Fuentes:** Vectorstore .parquet de los Reportes de **LIMS** y hojas de trabajo analiticas que documenten la precision intermedia.
        - **Objetivo especifico:** Registrar las replicas individuales de cada analista, asi como los calculos de %RSD, para cada API.
        - **Plan de accion:**
          1. Para cada API, procesa primero los .parquet de los reportes LIMS: extrae cada una de las filas "Solucion Muestra n" y captura los porcentajes del analista correspondiente A1D1E1 o A2D1E1 (Puedes usar esto en las consultas).
          2. Luego de esto usa el vectostore .parquet del reporte LIMS para recuperar los calculos consolidados (`rsd_an1_an2`) y cualquier referencia de corrida. Si el reporte no provee el dato, deja el campo en `null` pero registra en `issues` que debe calcularse en el razonamiento.
          3. Propaga el criterio recuperado en la Fase 1 hacia cada API. Si el LIMS incluye identificadores de corrida o notas relevantes, registralos en la trazabilidad interna.
        - **Normalizacion y control de calidad:**
          - Usa punto decimal y convierte todos los porcentajes a `float`.
          - Conserva exactamente los nombres de replicas y APIs.
          - No promedies ni elimines replicas salvo que esten claramente vacias; registra cualquier limpieza en las notas de trazabilidad.
          - Los campos `porcentaje_an1`, `porcentaje_an2`, `rsd_an1_an2` son obligatorios para validar el modelo; si alguno falta tras agotar las busquedas, reportalo en `issues` y evita generar un registro invalido.
          - Aprovecha el campo `issues` para describir cualquier documento faltante o diferencia detectada.
        - **Trazabilidad obligatoria (registro interno, no en la salida):** `source_document`, `page_or_span`, `query_used`, `confidence`, `cleaning_notes`.
        - **Control adicional:** Si existen varias corridas para la misma combinacion (API, analista, replica), prioriza la mas reciente/completa y deja constancia del criterio de deduplicacion.

  -----

    - **Ejemplo de extraccion completa (Set7ExtractionModel):**
      ```json
      {
        "activos_precision_intermedia": [
          {
            "nombre": "[API_PRINCIPAL]",
            "precision_intermedia": [
              { "replica": "Solucion Muestra 1", "porcentaje_an1": 100.2, "porcentaje_an2": 99.8 },
              { "replica": "Solucion Muestra 2", "porcentaje_an1": 100.1, "porcentaje_an2": 100.0 },
              { "replica": "Solucion Muestra 3", "porcentaje_an1": 99.9, "porcentaje_an2": 100.3 },
              { "replica": "Solucion Muestra 4", "porcentaje_an1": 100.4, "porcentaje_an2": 100.1 },
              { "replica": "Solucion Muestra 5", "porcentaje_an1": 99.7, "porcentaje_an2": 99.9 },
              { "replica": "Solucion Muestra 6", "porcentaje_an1": 100.0, "porcentaje_an2": 100.2 }
            ],
            "rsd_an1_an2": 0.58,
            "criterio_precision_intermedia": "Aceptar si %RSD <= 2.0% y |diferencia promedio| <= 2.0%."
          },
          {
            "nombre": "[API_SECUNDARIO]",
            "precision_intermedia": [
              { "replica": "Solucion Muestra 1", "porcentaje_an1": 101.1, "porcentaje_an2": 100.5 },
              { "replica": "Solucion Muestra 2", "porcentaje_an1": 101.4, "porcentaje_an2": 101.2 },
              { "replica": "Solucion Muestra 3", "porcentaje_an1": 100.8, "porcentaje_an2": 101.0 },
              { "replica": "Solucion Muestra 4", "porcentaje_an1": 101.0, "porcentaje_an2": 100.7 },
              { "replica": "Solucion Muestra 5", "porcentaje_an1": 101.3, "porcentaje_an2": 101.1 },
              { "replica": "Solucion Muestra 6", "porcentaje_an1": 101.5, "porcentaje_an2": 101.3 }
            ],
            "rsd_an1_an2": 0.72,
            "criterio_precision_intermedia": "Aceptar si %RSD <= 2.5% y |diferencia promedio| <= 2.0%."
          }
        ]
      }
      ```
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <br>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al `reasoning_agent`.

    - **Proposito:** Determinar, para cada API, si la precision intermedia cumple los criterios del protocolo y preparar los datos requeridos por `Set7StructuredOutputSupervisor`.
    - **Herramientas restringidas:** No utilices `linealidad_tool`; esta herramienta es exclusiva de `RULES_SET_3`.
    - **Entradas:** Objeto JSON completo producido por el `structured_extraction_agent`.
    - **Pasos del razonamiento:**
      1.  Verifica la consistencia de replicas y analistas. Si falta algun dato clave, registralo y explica como impacta el calculo.
      2.  Calcula el promedio global por analista (`promedio_an1`, `promedio_an2`) usando todas las replicas disponibles para el API.
      3.  Calcula `diferencia_promedio_an1_an2`, tomando la diferencia absoluta de los promedios obtenidos.
      4.  Calcula el `%RSD` combinado entre analistas cuando el LIMS no lo reporto. Justifica el metodo usado (p. ej. RSD del promedio de ambos analistas).
      5.  Compara los valores calculados con el criterio literal del protocolo. Documenta explicitamente los umbrales aplicados antes de decidir.
      6.  Determina `conclusion` por API: "Cumple" solo si cada condicion evaluada se encuentra dentro de los limites del protocolo; de lo contrario, "No Cumple".
      7.  Prepara los promedios globales para replicarlos en el campo `promedio_analistas` de cada replica, manteniendo dos decimales.
    - **Mini-ejemplo (orden recomendado):**
      - `[API_PRINCIPAL]`: promedio_an1=100.05; promedio_an2=100.05; diferencia=0.00%; RSD=0.58% vs criterio (%RSD <=2.0% y diferencia<=2.0%) -> Cumple.
      - `[API_SECUNDARIO]`: promedio_an1=101.18; promedio_an2=100.97; diferencia=0.21%; RSD=0.72% vs criterio (%RSD <=2.5% y diferencia<=2.0%) -> Cumple.
  </REGLAS_DE_RAZONAMIENTO>

  <br>

  <REGLAS_DE_SALIDA_SUPERVISOR>
  Aplica al `supervisor_agent`.

    - **Modelo de salida obligatorio:** `Set7StructuredOutputSupervisor`.
    - **Formato:** Emite un unico objeto JSON valido; ninguna frase adicional despues del razonamiento.
    - **Integracion de datos:**
      - Replica cada registro de `precision_intermedia` agregando `promedio_analistas` con un unico objeto `{ "promedio_an1": <valor>, "promedio_an2": <valor> }`.
      - Completa `rsd_an1_an2`, `diferencia_promedio_an1_an2` y `conclusion` utilizando los valores calculados por el razonamiento.
      - Incluye `criterio_precision_intermedia` como texto literal por API y anade `referencia_precision_intermedia` con la referencia analitica pertinente al conjunto de datos.
    - **Ejemplo de salida final del supervisor (tras documentar el razonamiento):**
      ```json
      {
        "activos_precision_intermedia": [
          {
            "nombre": "[API_PRINCIPAL]",
            "precision_intermedia": [
              {
                "replica": "Solucion Muestra 1",
                "porcentaje_an1": 100.2,
                "porcentaje_an2": 99.8,
              },
              {
                "replica": "Solucion Muestra 2",
                "porcentaje_an1": 100.1,
                "porcentaje_an2": 100.0,
              },
              {
                "replica": "Solucion Muestra 3",
                "porcentaje_an1": 99.9,
                "porcentaje_an2": 100.3,
              },
              {
                "replica": "Solucion Muestra 4",
                "porcentaje_an1": 100.4,
                "porcentaje_an2": 100.1,
              },
              {
                "replica": "Solucion Muestra 5",
                "porcentaje_an1": 99.7,
                "porcentaje_an2": 99.9,
              },
              {
                "replica": "Solucion Muestra 6",
                "porcentaje_an1": 100.0,
                "porcentaje_an2": 100.2,
              }
            ],
            "conclusion": "Cumple",
            "rsd_an1_an2": 0.58,
            "promedio_an1": 100.05,
            "promedio_an2": 100.05,            
            "diferencia_promedios_an1_an2": 0.00,
            "criterio_precision_intermedia": "Aceptar si %RSD <= 2.0% y |diferencia promedio| <= 2.0%."
          },
          {
            "nombre": "[API_SECUNDARIO]",
            "precision_intermedia": [
              {
                "replica": "Solucion Muestra 1",
                "porcentaje_an1": 101.1,
                "porcentaje_an2": 100.5,
              },
              {
                "replica": "Solucion Muestra 2",
                "porcentaje_an1": 101.4,
                "porcentaje_an2": 101.2,
              },
              {
                "replica": "Solucion Muestra 3",
                "porcentaje_an1": 100.8,
                "porcentaje_an2": 101.0,
              },
              {
                "replica": "Solucion Muestra 4",
                "porcentaje_an1": 101.0,
                "porcentaje_an2": 100.7,
              },
              {
                "replica": "Solucion Muestra 5",
                "porcentaje_an1": 101.3,
                "porcentaje_an2": 101.1,
              },
              {
                "replica": "Solucion Muestra 6",
                "porcentaje_an1": 101.5,
                "porcentaje_an2": 101.3,
              }
            ],
            "conclusion": "Cumple",
            "rsd_an1_an2": 0.72,
            "promedio_an1": 101.18,
            "promedio_an2": 100.97,
            "diferencia_promedios_an1_an2": 0.22,
            "criterio_precision_intermedia": "Aceptar si %RSD <= 2.5% y |diferencia promedio| <= 2.0%."
          }
        ],
        "referencia_precision_intermedia": "[ID_CORRIDA_PRECISION_INTERMEDIA]"
      }
      ```
    - **Recordatorio estricto:** El razonamiento completo debe preceder al JSON final; incluye todos los calculos (promedios, diferencias, RSD, criterios) antes de presentar la salida estructurada.
  </REGLAS_DE_SALIDA_SUPERVISOR>
"""

RULES_SET_8 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer y estructurar el criterio de aceptación y la información de **estabilidad de soluciones de estandar y muestra** para cada **analito**, mediante un proceso en dos fases. SIEMPRE DEBES EJECUTAR LAS 2 FASES.. ES OBLIGATORIO!!
      - DEBES planificar exhaustivamente antes de cada llamada a una función y reflexionar exhaustivamente sobre los resultados de las llamadas a las funciones anteriores. NO realices todo este proceso haciendo solo llamadas a funciones, ya que esto puede afectar tu capacidad para resolver el problema y pensar de manera perspicaz.

  -----

    - **Fase 1: Extracción de criterios de aceptación del protocolo de validación**
        - **Fuente primaria:** Documento del **Protocolo de Validación** en vectorstore .parquet.
        - **Objetivo específico:** Identificar los criterios de aceptación del parámetro estabilidad de las soluciones.
        - **Plan de acción:**
          1.  Genera consultas sobre el vectorstore .parquet del protocolo de validación con strings similares a "Criterio de aceptación de Estabilidad de soluciones".
          2.  Extrae el texto más completo y descriptivo que encuentres en los chunks de los criterios de aceptación de la tabla "Criterio de aceptación" de la estabilidad de las soluciones del protocolo de validación.
          3.  Registra el string con el criterio de aceptación de acuerdo a lo reportado en el texto extraído.
        - **Ejemplo de salida :**
        ```json
        {
            "criterio_aceptacion": "CRITERIO_DEL_PROTOCOLO"
        }
        ```

  -----

    - **Fase 2: Inventario de analitos en los reportes**
        - **Fuentes:** Documento del reporte LIMS o Soluciones en vectorstore .parquet.
        - **Objetivo:** Enumerar cada analito presente en los reportes y datos asociados antes de iniciar la Fase 2.
        - **Plan de acción:**
          1.  Recorre los chunks de datos extraidos del reporte LIMS o Soluciones en vectorstore .parquet con la clave "analito". Anota cada uno de los analitos que identifiques en estos chunks
          2.  Construye una lista ordenada de analitos.
        - **Ejemplo de salida :**
        ```json
        {
            "analitos": [
                {
                    "analito": "ANALITO_1"
                },
                {
                    "analito": "ANALITO_2"
                }
            ]
        }
        ```

  -----

    - **Fase 3: Extracción de datos experimentales (reporte LIMS / estabilidad soluciones, entre otros)**
          - **Fuentes:** Documentos del reporte LIMS o Soluciones en vectorstore .parquet.
          - **Objetivo específico:** Extraer todas las réplicas individuales, promedios y diferencias para cada analito, solución, condición y tiempo reportado.
          - **Plan de acción:**
            1.  **Bucle por analito:** Itera sobre la lista generada de analitos en la fase 2 y deja constancia del analito activo antes de lanzar consultas. Ejecuta los siguientes pasos por cada una de las etapas de esta lista.. Siempre dejando claramente en un mensaje de texto lo que pudiste extraer.
              1.1 Genera al menos 20 consultas sobre el vectorsore .parquet del reporte de Estabilidad de las Soluciones, que combinen el nombre del analito activo con patrones como "tipo_solucion", "condicion_estabilidad", "tiempo_estabilidad", "Solucion_Muestra", y "Solucion_Estandar".
              1.2 Del texto recuperado, identifica un listado de las soluciones que tiene este analito, esto es, si tiene "Solucion Muestra" y/o "Solucion Estandar".
              1.3 Por cada solucion, esto es, si es "Solucion Estandar" y/o "Solucion Muestra" identifica, cuantos tiempos tiene y cuales son.
              1.4 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) identifica, bajo cuantas condiciones fueron evaluadas.
              1.5 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) y cada condicion ("Condicion 1", "Condicion 2", etc.) identifica, cuantas réplicas se reportaron.
              1.6 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) y cada condicion ("Condicion 1", "Condicion 2", etc.) y por cada replica, identifica el valor del resultado de Area indicado en el reporte.
              1.7 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) identifica el promedio de los datos de la solucion bajo las diferentes condiciones que fueron evaluadas las muestras.
              1.8 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) identifica el %di o % similitud de los datos de la solucion bajo las diferentes condiciones que fueron evaluadas las muestras.
              1.9 Por cada solucion ("Solucion Estandar" y/o "Solucion Muestra") y cada tiempo ("Initial Sample", "Tiempo 1", "Tiempo 2", etc.) identificala referencia analítica, esto es, el código iniciado en HT... que se mostró en el reporte.
              1.10 Consolida en un mensaje los resultados extraidos por analito y sigue con el siguiente analito en la búsqueda. DEBES EJECUTAR LAS BÚSQUEDAS CON EL SIGUIENTE ANALITO CON EL MISMO NIVEL DE RIGUROSIDAD QUE LO HICISTE CON ESTE.. NO OIMTAS NINGUNA INSTRUCCION RELEVANTE PARA ENSAMBLAR LAS CONSULTAS O PARA EXTRAER LA DATA.
            
            2. Ejemplo de extracción completa:
            **ADVERTENCIA: El siguiente ejemplo es ESTRUCTURAL. Todos los valores entre corchetes (ej. "[VALOR_PLACEHOLDER]") son placeholders genéricos. NO DEBEN ser copiados. El agente DEBE extraer los valores y nombres reales del documento fuente.**
            ```json
            {
              "activos_estabilidad_solucion": [
                {
                  "solucion": "SOLUCION_MUESTRA_ANALITO_A",
                  "tipo_solucion": "Solucion_Muestra",
                  "data_estabilidad_solucion": [
                    {
                      "analito": "NOMBRE_ANALITO_A",
                      "condicion_estabilidad": "CONDICION_INICIAL",
                      "tiempo_estabilidad": "TIEMPO_CERO",
                      "promedio_areas": "VALOR_NUMERICO_1",
                      "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_1",
                      "data_condicion": [
                        {
                          "replica": 1,
                          "area": "VALOR_NUMERICO_REPLICA_1A"
                        },
                        {
                          "replica": 2,
                          "area": "VALOR_NUMERICO_REPLICA_1B"
                        }
                      ],
                      "referencia_analitica": "CODIGO_REFERENCIA_HT_1"
                    },
                    {
                      "analito": "NOMBRE_ANALITO_A",
                      "condicion_estabilidad": "CONDICION_A_TIEMPO_1",
                      "tiempo_estabilidad": "TIEMPO_UNO",
                      "promedio_areas": "VALOR_NUMERICO_2",
                      "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_2",
                      "data_condicion": [
                        {
                          "replica": 1,
                          "area": "VALOR_NUMERICO_REPLICA_2A"
                        },
                        {
                          "replica": 2,
                          "area": "VALOR_NUMERICO_REPLICA_2B"
                        }
                      ],
                      "referencia_analitica": "CODIGO_REFERENCIA_HT_1"
                    }
                  ],
                  "criterios_validacion": [
                    {
                      "parametro": "DIFERENCIA_PORCENTUAL",
                      "criterio_aceptacion": "VALOR_CRITERIO_NUMERICO"
                    }
                  ]
                },
                {
                  "solucion": "SOLUCION_ESTANDAR_ANALITO_B",
                  "tipo_solucion": "Solucion_Estandar",
                  "data_estabilidad_solucion": [
                    {
                      "analito": "NOMBRE_ANALITO_B",
                      "condicion_estabilidad": "CONDICION_INICIAL",
                      "tiempo_estabilidad": "TIEMPO_CERO",
                      "promedio_areas": "VALOR_NUMERICO_3",
                      "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_3",
                      "data_condicion": [
                        {
                          "replica": 1,
                          "area": "VALOR_NUMERICO_REPLICA_3A"
                        },
                        {
                          "replica": 2,
                          "area": "VALOR_NUMERICO_REPLICA_3B"
                        }
                      ],
                      "referencia_analitica": "CODIGO_REFERENCIA_HT_2"
                    },
                    {
                      "analito": "NOMBRE_ANALITO_B",
                      "condicion_estabilidad": "CONDICION_B_TIEMPO_1",
                      "tiempo_estabilidad": "TIEMPO_UNO",
                      "promedio_areas": "VALOR_NUMERICO_4",
                      "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_4",
                      "data_condicion": [
                        {
                          "replica": 1,
                          "area": "VALOR_NUMERICO_REPLICA_4A"
                        },
                        {
                          "replica": 2,
                          "area": "VALOR_NUMERICO_REPLICA_4B"
                        }
                      ],
                      "referencia_analitica": "CODIGO_REFERENCIA_HT_2"
                    }
                  ],
                  "criterios_validacion": [
                    {
                      "parametro": "DIFERENCIA_PORCENTUAL",
                      "criterio_aceptacion": "VALOR_CRITERIO_NUMERICO"
                    }
                  ]
                }
              ],
              "referencia_analitica_estabilidad_soluciones": "CODIGO_REFERENCIA_GENERAL_HT"
            }
            ```
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <br>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al `reasoning_agent`.

    - **Propósito:** Verificar la estabilidad de cada solución de muestra frente a los criterios del protocolo y preparar la salida conforme al modelo `Set8StructuredOutputSupervisor`.
    - **Herramientas restringidas:** No utilices `linealidad_tool`; está prohibida para este conjunto.
    - **Entradas:** Objeto JSON generado por el `structured_extraction_agent`.
    - **Pasos del razonamiento:**
      1.  Para cada solución, identifica el valor de referencia (tiempo inicial) por condición.
      2.  Calcula `promedio_areas` y `diferencia_promedios` únicamente cuando existan réplicas suficientes; si no puedes derivarlos con certeza, deja los campos en `null`, registra el issue y no los sustituyas por 0.
      3.  Compara el valor absoluto de `diferencia_promedios` con el umbral literal de `criterio_aceptacion`, documentando cualquier cálculo auxiliar.
      4.  Define `conclusion_estabilidad`: "Cumple" solo si la variación cae dentro del umbral; si faltan métricas clave, marca "Pendiente" y referencia el issue.
      5.  Determina la `conclusion_estabilidad_muestra` global considerando solo las condiciones con datos completos. Si quedan condiciones pendientes, deja la conclusión global en "Pendiente" y explica la razón.
      6.  Resume explícitamente los cálculos, supuestos e issues antes de producir el JSON final.
  </REGLAS_DE_RAZONAMIENTO>

  <br>

  <REGLAS_DE_SALIDA_SUPERVISOR>
  Aplica al `supervisor_agent`.

    - **Modelo de salida obligatorio:** `Set8StructuredOutputSupervisor`.
    - **Formato:** Un solo objeto JSON bien formado sin texto extra tras el razonamiento.
    - **Integración de datos:**
      - Replica los bloques de `data_estabilidad_solucion` con los valores finales y conclusiones.
      - Mantén la lista `referencia_analitica` con todas las referencias relevantes.
      - No añadas campos nuevos; reporta únicamente los definidos en el modelo.
    - **Ejemplo de salida final del supervisor:**
      ```json
      {
        "activos_estabilidad_solucion": [
          {
            "solucion": "SOLUCION_MUESTRA_ANALITO_A",
            "tipo_solucion": "Solucion_Muestra",
            "data_estabilidad_solucion": [
              {
                "analito": "NOMBRE_ANALITO_A",
                "condicion_estabilidad": "CONDICION_INICIAL",
                "tiempo_estabilidad": "TIEMPO_CERO",
                "promedio_areas": "VALOR_NUMERICO_1",
                "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_1",
                "data_condicion": [
                  {
                    "replica": 1,
                    "area": "VALOR_NUMERICO_REPLICA_1A"
                  },
                  {
                    "replica": 2,
                    "area": "VALOR_NUMERICO_REPLICA_1B"
                  }
                ],
                "referencia_analitica": "CODIGO_REFERENCIA_HT_1"
              },
              {
                "analito": "NOMBRE_ANALITO_A",
                "condicion_estabilidad": "CONDICION_A_TIEMPO_1",
                "tiempo_estabilidad": "TIEMPO_UNO",
                "promedio_areas": "VALOR_NUMERICO_2",
                "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_2",
                "data_condicion": [
                  {
                    "replica": 1,
                    "area": "VALOR_NUMERICO_REPLICA_2A"
                  },
                  {
                    "replica": 2,
                    "area": "VALOR_NUMERICO_REPLICA_2B"
                  }
                ],
                "referencia_analitica": "CODIGO_REFERENCIA_HT_1"
              }
            ],
            "criterios_validacion": [
              {
                "parametro": "DIFERENCIA_PORCENTUAL",
                "criterio_aceptacion": "VALOR_CRITERIO_NUMERICO"
              }
            ]
          },
          {
            "solucion": "SOLUCION_ESTANDAR_ANALITO_B",
            "tipo_solucion": "Solucion_Estandar",
            "data_estabilidad_solucion": [
              {
                "analito": "NOMBRE_ANALITO_B",
                "condicion_estabilidad": "CONDICION_INICIAL",
                "tiempo_estabilidad": "TIEMPO_CERO",
                "promedio_areas": "VALOR_NUMERICO_3",
                "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_3",
                "data_condicion": [
                  {
                    "replica": 1,
                    "area": "VALOR_NUMERICO_REPLICA_3A"
                  },
                  {
                    "replica": 2,
                    "area": "VALOR_NUMERICO_REPLICA_3B"
                  }
                ],
                "referencia_analitica": "CODIGO_REFERENCIA_HT_2"
              },
              {
                "analito": "NOMBRE_ANALITO_B",
                "condicion_estabilidad": "CONDICION_B_TIEMPO_1",
                "tiempo_estabilidad": "TIEMPO_UNO",
                "promedio_areas": "VALOR_NUMERICO_4",
                "diferencia_promedios": "VALOR_NUMERICO_CALCULADO_4",
                "data_condicion": [
                  {
                    "replica": 1,
                    "area": "VALOR_NUMERICO_REPLICA_4A"
                  },
                  {
                    "replica": 2,
                    "area": "VALOR_NUMERICO_REPLICA_4B"
                  }
                ],
                "referencia_analitica": "CODIGO_REFERENCIA_HT_2"
              }
            ],
            "criterios_validacion": [
              {
                "parametro": "DIFERENCIA_PORCENTUAL",
                "criterio_aceptacion": "VALOR_CRITERIO_NUMERICO"
              }
            ]
          }
        ],
        "referencia_analitica_estabilidad_soluciones": "CODIGO_REFERENCIA_GENERAL_HT",
        "conclusion_estabilidad_soluciones": "CONCLUSION_GENERADA_AUTOMATICAMENTE_SOBRE_SI_LOS_DATOS_DE_AMBOS_ANALITOS_CUMPLEN_O_NO_CON_LOS_CRITERIOS"
      }
      ```
  </REGLAS_DE_SALIDA_SUPERVISOR>
"""

RULES_SET_10 = """
  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al `reasoning_agent`.

  - **Propósito:** Calcular las estadísticas, aplicar los criterios de aceptación y determinar las conclusiones para cada parámetro y analito, poblando completamente el modelo `Set10StructuredOutput`.
  - **Entradas:** Objeto JSON generado por el `structured_extraction_agent`.
  - **Pasos del razonamiento:**
      1.  **Itera por cada analito** en la lista `analitos`.
      2.  **Itera por cada `resultados_por_tiempo`** dentro de ese analito.
      3.  **Calcular Estadísticas:**
          - Usa los valores en `replicas_data` para calcular: `promedio_areas_system`, `promedio_tiempo_retencion`, `promedio_usp_tailing`.
          - Calcula el `rsd_areas_system` (RSD en porcentaje).
          - Actualiza estos campos en el objeto `resultados_por_tiempo`.
      4.  **Aplicar Criterios y Concluir:**
          - **RSD de Áreas:** Compara el `rsd_areas_system` calculado con el umbral del criterio. Define `conclusion_rsd_areas` como "Cumple" o "No Cumple".
          - **USP Tailing:** Compara el `promedio_usp_tailing` con su criterio. Define `conclusion_usp_tailing` como "Cumple" o "No Cumple".
          - **Tiempo de Retención:** Compara los promedios entre tiempos si el criterio lo exige. Define `conclusion_tiempo_retencion`.
      5.  **Conclusión General:** Una vez evaluados todos los tiempos para un analito, determina la `conclusion_general_analito`. Será "Cumple" solo si todas las conclusiones individuales son "Cumple".
      6.  **Narrativa:** Antes de la salida, resume los cálculos clave. Ej: "Para [NOMBRE_ANALITO_1] en [ETIQUETA_TIEMPO_0], el RSD de áreas fue [VALOR_CALCULADO]%, que cumple el criterio de '[CRITERIO]%', por lo tanto Cumple."

  </REGLAS_DE_RAZONAMIENTO>

  <br>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  - **Modelo de salida obligatorio:** `Set10StructuredOutput`.
  - **Formato:** Un único objeto JSON bien formado y completo, sin texto adicional.
  - **Integración de datos:**
      - El objeto final debe contener todos los datos extraídos, los valores calculados y las conclusiones finales generadas por el `reasoning_agent`.
      - No añadas campos que no estén definidos en el modelo `Set10StructuredOutput`.
  - **Ejemplo de Salida Final del Supervisor (Data-Agnóstico):**
      ```json
      {
        "titulo_parametro": "Resultados Estabilidad de la Fase Móvil",
        "analitos": [
          {
            "nombre_analito": "[NOMBRE_ANALITO_1]",
            "resultados_por_tiempo": [
              {
                "tiempo_label": "[ETIQUETA_TIEMPO_0]",
                "replicas_data": [
                  { "replica": 1, "areas_system": "[VALOR_NUMERICO]", "tiempo_retencion": "[VALOR_NUMERICO]", "usp_tailing": "[VALOR_NUMERICO]" },
                  { "replica": 2, "areas_system": "[VALOR_NUMERICO]", "tiempo_retencion": "[VALOR_NUMERICO]", "usp_tailing": "[VALOR_NUMERICO]" },
                  { "replica": 3, "areas_system": "[VALOR_NUMERICO]", "tiempo_retencion": "[VALOR_NUMERICO]", "usp_tailing": "[VALOR_NUMERICO]" }
                ],
                "promedio_areas_system": "[VALOR_CALCULADO]",
                "promedio_tiempo_retencion": "[VALOR_CALCULADO]",
                "promedio_usp_tailing": "[VALOR_CALCULADO]",
                "rsd_areas_system": "[VALOR_CALCULADO]",
                "conclusion_rsd_areas": "[CONCLUSION_PARAMETRO]",
                "conclusion_tiempo_retencion": "[CONCLUSION_PARAMETRO]",
                "conclusion_usp_tailing": "[CONCLUSION_PARAMETRO]"
              },
              {
                "tiempo_label": "[ETIQUETA_TIEMPO_1]",
                "replicas_data": [
                  { "replica": 1, "areas_system": "[VALOR_NUMERICO]", "tiempo_retencion": "[VALOR_NUMERICO]", "usp_tailing": "[VALOR_NUMERICO]" },
                  { "replica": 2, "areas_system": "[VALOR_NUMERICO]", "tiempo_retencion": "[VALOR_NUMERICO]", "usp_tailing": "[VALOR_NUMERICO]" }
                ],
                "promedio_areas_system": "[VALOR_CALCULADO]",
                "promedio_tiempo_retencion": "[VALOR_CALCULADO]",
                "promedio_usp_tailing": "[VALOR_CALCULADO]",
                "rsd_areas_system": "[VALOR_CALCULADO]",
                "conclusion_rsd_areas": "[CONCLUSION_PARAMETRO]",
                "conclusion_tiempo_retencion": "[CONCLUSION_PARAMETRO]",
                "conclusion_usp_tailing": "[CONCLUSION_PARAMETRO]"
              }
            ],
            "criterios_aceptacion": [
              { "parametro": "[NOMBRE_PARAMETRO_1]", "criterio": "[DESCRIPCION_LITERAL_CRITERIO_1]" },
              { "parametro": "[NOMBRE_PARAMETRO_2]", "criterio": "[DESCRIPCION_LITERAL_CRITERIO_2]" }
            ],
            "conclusion_general_analito": "[CONCLUSION_GENERAL]"
          }
        ],
        "referencia_analitica": "[CODIGO_REFERENCIA_HT]"
      }
      ```
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
"""


RULES_SET_11 = """

  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al `structured_extraction_agent`.

    - **Objetivo General:** Extraer y estructurar la información de **robustez** por API en dos fases, conforme al modelo `Set11ExtractionModel`.

  -----

    - **Fase 1: Extracción de criterios y factores del protocolo**

        - **Fuente primaria:** Documento del **Protocolo de Validación** (tabla de condiciones de robustez).
        - **Objetivo específico:** Registrar los factores modificados, sus niveles nominales/ajustados y el criterio de aceptación global.
        - **Plan de acción:**
          1.  Ubica la tabla de "Condiciones de robustez" o equivalente.
          2.  Extrae para cada experimento los valores objetivo (temperatura, flujo, volumen de inyección, composición de fase móvil, etc.) y puebla `experimento_robustez`.
          3.  Transcribe el criterio literal (ej.: `|%di| <= 2.0%`, `No debe cambiar el orden de elución`) y almacénalo en `criterio_robustez` para cada API.
        - **Salida esperada Fase 1 (ejemplo sintético):**
          ```json
          {
            "activos_robustez": [
              {
                "nombre": "[API_1]",
                "criterio_robustez": "Aceptar si |%di| <= 2.0% para cada condición evaluada."
              }
            ],
            "referencia_robustez": "[ID_PROTOCOLO]",
            "experimento_robustez": [
              { "nombre_experimento": "Flow", "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" }
            ]
          }
          ```

  -----

    - **Fase 2: Extracción de datos experimentales (reportes analíticos / LIMS)**

        - **Fuentes:** Reportes analíticos finales y/o LIMS que contengan secciones "Robustness Flow/Temperature/Injection Volume/Mobile Phase".
        - **Objetivo específico:** Capturar las réplicas individuales, los promedios por condición y las diferencias porcentuales respecto a la condición nominal para cada API.
        - **Plan de acción:**
          1.  Identifica bloques que agrupen réplicas por experimento y condición (Nominal, Bajo, Alto, etc.).
          2.  Registra cada réplica en la lista `robustez`, conservando el texto literal del experimento (ej.: "Robustness Flow - Bajo").
          3.  Transcribe `promedio_experimento` y `diferencia_porcentaje` si el reporte los provee; si faltan, deja `null` y anota en la trazabilidad que se calcularán en el razonamiento.
          4.  Marca `conclusion_robustez` como `[pendiente_validar]` hasta que se evalúe en el razonamiento.
          5.  Asegura que la `referencia_robustez` y los factores de `experimento_robustez` estén presentes en la raíz del objeto.
        - **Normalización y control de calidad:**
          - Elimina símbolos de porcentaje; usa punto decimal.
          - `replica` debe ser entero correlativo.
          - Si se detectan múltiples corridas para el mismo API/condición, prioriza la más completa y documenta el criterio.
        - **Trazabilidad obligatoria (registro interno, no en la salida):** `source_document`, `page_or_span`, `query_used`, `confidence`, `cleaning_notes`.

  -----

    - **Ejemplo de extracción completa (Set11ExtractionModel):**
      ```json
      {
        "activos_robustez": [
          {
            "nombre": "[API_1]",
            "robustez": [
              { "experimento": "Robustness Flow - Nominal", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Bajo", "replica": 1, "valores_aproximados": 99.6, "promedio_experimento": 99.6, "diferencia_porcentaje": -0.50 },
              { "experimento": "Robustness Flow - Alto", "replica": 1, "valores_aproximados": 100.7, "promedio_experimento": 100.7, "diferencia_porcentaje": 0.60 },
              { "experimento": "Robustness Temperature - Nominal", "replica": 1, "valores_aproximados": 100.3, "promedio_experimento": 100.3, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Temperature - Alto", "replica": 1, "valores_aproximados": 100.9, "promedio_experimento": 100.9, "diferencia_porcentaje": 0.60 }
            ],
            "conclusion_robustez": "[pendiente_validar]",
            "criterio_robustez": "Aceptar si |%di| <= 2.0% para todas las condiciones."
          },
          {
            "nombre": "[API_2]",
            "robustez": [
              { "experimento": "Robustness Flow - Nominal", "replica": 1, "valores_aproximados": 99.8, "promedio_experimento": 99.9, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 99.9, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Bajo", "replica": 1, "valores_aproximados": 99.4, "promedio_experimento": 99.5, "diferencia_porcentaje": -0.40 },
              { "experimento": "Robustness Flow - Alto", "replica": 1, "valores_aproximados": 100.5, "promedio_experimento": 100.4, "diferencia_porcentaje": 0.50 },
              { "experimento": "Robustness Mobile Phase - Nominal", "replica": 1, "valores_aproximados": 99.7, "promedio_experimento": 99.7, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Mobile Phase - Variante B", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.2, "diferencia_porcentaje": 0.50 }
            ],
            "conclusion_robustez": "[pendiente_validar]",
            "criterio_robustez": "Aceptar si |%di| <= 2.5% para cada condición de robustez."
          }
        ],
        "referencia_robustez": "[HTA_ROBUSTEZ]",
        "experimento_robustez": [
          { "nombre_experimento": "Flow", "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
          { "nombre_experimento": "Temperature", "temperatura": 35.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
          { "nombre_experimento": "Mobile Phase", "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x1]:ACN [y1]" }
        ]
      }
      ```
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <br>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al `reasoning_agent`.

    - **Propósito:** Evaluar si cada API cumple los criterios de robustez del protocolo comparando las condiciones modificadas contra la condición nominal y preparar la salida para `Set11StructuredOutputSupervisor`.
    - **Herramientas restringidas:** No utilices `linealidad_tool`; está prohibida en este conjunto.
    - **Entradas:** Objeto JSON producido por el `structured_extraction_agent`.
    - **Pasos del razonamiento:**
      1.  Agrupa las réplicas por API y experimento, identificando claramente la condición nominal.
      2.  Calcula `promedio_experimento` y `diferencia_porcentaje` si se dejaron en `null`, documentando el método.
      3.  Para cada condición distinta de la nominal, calcula `%di = 100 * (promedio_condicion - promedio_nominal) / promedio_nominal` y registra el resultado antes de compararlo.
      4.  Compara cada `%di` con el criterio literal (`criterio_robustez`). Si el criterio incluye otras verificaciones (ej. orden de elución), deja evidencia textual del chequeo.
      5.  Determina `conclusion_robustez` por API: "Cumple" únicamente si todas las condiciones evaluadas satisfacen los límites; de lo contrario, "No Cumple".
      6.  Resume en la narrativa los valores clave (promedio nominal, %di por condición, umbral aplicado) antes de emitir la conclusión.
      7.  Señala cualquier dato faltante o supuesto que pueda afectar la interpretación.
    - **Mini-ejemplo (orden recomendado):**
      - `[API_1] Flow Bajo`: promedio_nominal=100.1; promedio_bajo=99.6; %di=-0.50% (<=2.0%) -> Cumple.
      - `[API_1] Flow Alto`: %di=+0.60% (<=2.0%) -> Cumple.
      - `[API_2] Mobile Phase Variante B`: %di=+0.50% (<=2.5%) -> Cumple. Conclusión global API_2 = "Cumple".
  </REGLAS_DE_RAZONAMIENTO>

  <br>

  <REGLAS_DE_SALIDA_SUPERVISOR>
  Aplica al `supervisor_agent`.

    - **Modelo de salida obligatorio:** `Set11StructuredOutputSupervisor`.
    - **Formato:** único objeto JSON bien formado; no se permite texto adicional tras el razonamiento.
    - **Integración de datos:**
      - Copia las réplicas de `robustez` incorporando los valores calculados definitivos.
      - Actualiza `conclusion_robustez` y `criterio_robustez` por API según el análisis.
      - Convierte `experimento_robustez` a `experimentos_robustez` conservando los factores del protocolo.
      - Mantén `referencia_robustez` literal.
    - **Ejemplo de salida final del supervisor:**
      ```json
      {
        "activos_robustez": [
          {
            "nombre": "[API_1]",
            "robustez": [
              { "experimento": "Robustness Flow - Nominal", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Bajo", "replica": 1, "valores_aproximados": 99.6, "promedio_experimento": 99.6, "diferencia_porcentaje": -0.50 },
              { "experimento": "Robustness Flow - Alto", "replica": 1, "valores_aproximados": 100.7, "promedio_experimento": 100.7, "diferencia_porcentaje": 0.60 },
              { "experimento": "Robustness Temperature - Nominal", "replica": 1, "valores_aproximados": 100.3, "promedio_experimento": 100.3, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Temperature - Alto", "replica": 1, "valores_aproximados": 100.9, "promedio_experimento": 100.9, "diferencia_porcentaje": 0.60 }
            ],
            "conclusion_robustez": "Cumple",
            "criterio_robustez": "Aceptar si |%di| <= 2.0% para todas las condiciones."
          },
          {
            "nombre": "[API_2]",
            "robustez": [
              { "experimento": "Robustness Flow - Nominal", "replica": 1, "valores_aproximados": 99.8, "promedio_experimento": 99.9, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 99.9, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Flow - Bajo", "replica": 1, "valores_aproximados": 99.4, "promedio_experimento": 99.5, "diferencia_porcentaje": -0.40 },
              { "experimento": "Robustness Flow - Alto", "replica": 1, "valores_aproximados": 100.5, "promedio_experimento": 100.4, "diferencia_porcentaje": 0.50 },
              { "experimento": "Robustness Mobile Phase - Nominal", "replica": 1, "valores_aproximados": 99.7, "promedio_experimento": 99.7, "diferencia_porcentaje": 0.0 },
              { "experimento": "Robustness Mobile Phase - Variante B", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.2, "diferencia_porcentaje": 0.50 }
            ],
            "conclusion_robustez": "Cumple",
            "criterio_robustez": "Aceptar si |%di| <= 2.5% para cada condición de robustez."
          }
        ],
        "referencia_robustez": "[HTA_ROBUSTEZ]",
        "experimentos_robustez": [
          { "nombre_experimento": "Flow", "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
          { "nombre_experimento": "Temperature", "temperatura": 35.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
          { "nombre_experimento": "Mobile Phase", "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x1]:ACN [y1]" }
        ]
      }
      ```
    - **Recordatorio estricto:** El razonamiento debe documentar cálculos, umbrales y conclusiones antes de presentar el JSON final.
  </REGLAS_DE_SALIDA_SUPERVISOR>

"""