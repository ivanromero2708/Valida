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
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al structured_extraction_agent.

  - Objetivo: Extraer y estructurar la **estabilidad de soluciones** (estándar y muestra) desde reportes LIMS y protocolo, conforme a `Set8ExtractionModel`.

  - Plan iterativo (varios ciclos sobre el vectorstore):
    1) Descubrimiento de soluciones: buscar tablas por patrón de tiempos (“Initial Sample Stability”, “Sample Stability Time 1..n”) y réplicas (“Solucion Estandar/Muestra R1..R3”) separadas por **Condición 1** y **Condición 2**.
    2) Extracción por solución (subciclo por cada solución encontrada):
      • Construir `data_estabilidad_solucion` como lista de entradas por (tiempo_estabilidad, condición_estabilidad).  
      • Para cada entrada:
        - `data_condicion` ← lista de {replica:int, area:float} recolectada de las réplicas R1..R3.  
        - `promedio_areas` ← si el LIMS lo reporta (“Promedio Solucion ...”), guardarlo; si falta, dejar "[pendiente_calcular]".  
        - `diferencia_promedios` ← si el LIMS lo reporta como “%di ...”, guardarlo; si falta, "[pendiente_calcular]".  
        - `criterio_aceptacion` ← extraer del Protocolo (umbral de variación permisible vs. tiempo inicial; registrar literal).  
        - `conclusion_estabilidad` ← inicializar "[pendiente_validar]".
    3) Trazabilidad obligatoria (ledger interno, no en la salida): source_document (LIMS/Protocolo), page_or_span, query_used, confidence, cleaning_notes.
    4) Normalización mínima:
      • Decimales coma→punto; áreas y promedios como float.  
      • Tiempos con literal exacto del LIMS.  
      • `replica` entero ≥1; eliminar filas incompletas (sin área) con motivo documentado.
    5) Deduplificación: si hay múltiples corridas, unificar por (solución, tiempo, condición, réplica, run_id) conservando la más completa/reciente.
    6) Relleno de huecos: tras los ciclos, los campos faltantes permanecen con "[pendiente_calcular]" o "[pendiente_validar]" y se deja constancia en trazabilidad.

  - Ejemplo de extracción estructurada (Set8ExtractionModel con placeholders):
  {
    "soluciones": [
      {
        "solucion": "[Solucion Estandar X]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 250000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 249800.0 },
              { "replica": 2, "area": 250100.0 },
              { "replica": 3, "area": 250100.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 2",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 249900.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 249700.0 },
              { "replica": 2, "area": 250000.0 },
              { "replica": 3, "area": 250000.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Sample Stability Time 1",
            "promedio_areas": "[pendiente_calcular]",
            "diferencia_promedios": "[pendiente_calcular]",
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 249300.0 },
              { "replica": 2, "area": 249900.0 },
              { "replica": 3, "area": 249800.0 }
            ]
          }
        ]
      },
      {
        "solucion": "[Solucion Muestra Y]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 310000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 309600.0 },
              { "replica": 2, "area": 310100.0 },
              { "replica": 3, "area": 310300.0 }
            ]
          }
        ]
      }
    ],
    "referencia_analitica": ["[HT00XXXXXX]", "[METODO-REF-YY]"],
    "conclusion_estabilidad_muestra": "[pendiente_validar]"
  }
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al reasoning_agent.

  - RESTRICCIÓN CLAVE: Documentar el razonamiento **antes** de cualquier conclusión o salida.

  - Pasos por solución (explicitar cálculos e inferencias):
    1) Agrupar por (tiempo_estabilidad, condición) y verificar N réplicas válidas (≥3 usualmente); listar las áreas usadas.
    2) Cálculos intermedios:
      • Si `promedio_areas` = "[pendiente_calcular]": promedio = mean(áreas).  
      • Para cada (tiempo, condición), calcular %di respecto al **promedio del tiempo inicial de la misma condición**:  
        %di = 100 * abs(promedio_t - promedio_t0) / promedio_t0.  
        Guardar como `diferencia_promedios` si venía "[pendiente_calcular]".
    3) Comparación con criterio:
      • Extraer umbral desde `criterio_aceptacion` (ej. “|%di| <= 2.0%”).  
      • Para cada (tiempo, condición): si |%di| ≤ umbral → “Cumple”; si no → “No Cumple”. Rellenar `conclusion_estabilidad`.
    4) Conclusión global de la muestra:
      • `conclusion_estabilidad_muestra` = "Cumple" si **todas** las entradas de esa solución cumplen; de lo contrario "No Cumple".  
      • Si el set requiere una sola conclusión global para todas las soluciones, usar AND lógico entre soluciones y dejar nota del criterio aplicado.
    5) Documentar: valores de t0, promedios por tiempo, %di por condición y umbral aplicado.

  - Mini-ejemplo de razonamiento (orden correcto):
    • Condición 1 (t0): promedio_t0 = 250000.0  
    • Condición 1 (t1): promedio_t1 = 249667.0 → %di = 100*|249667-250000|/250000 = 0.133%  
    • Umbral = 2.0% → Cumple en t1; todas las entradas cumplen → conclusión solución = “Cumple”.  
    • Todas las soluciones cumplen → `conclusion_estabilidad_muestra` = “Cumple”.
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  Estas reglas aplican al supervisor.

  - Modelo de salida: `Set8StructuredOutputSupervisor` en JSON bien formado. **Emitir solo el JSON final**, después de documentar el razonamiento.
  - Integración:
    • Completar `promedio_areas` y `diferencia_promedios` si fueron calculados.  
    • Fijar `conclusion_estabilidad` por (tiempo, condición).  
    • Determinar `conclusion_estabilidad_muestra` (global).  
    • Mantener `referencia_analitica`.

  - Ejemplo A (caso global “Cumple”) — Orden: 1) razonamiento → 2) salida
  Razonamiento (resumen): Para [Solucion Estandar X], C1: t0=250000.0; t1=249667.0 → %di=0.133% (≤2.0%). C2: t0=249900.0; t1=249733.3 → %di=0.067% (≤2.0%). Para [Solucion Muestra Y], C1: t0=310000.0; t1=309700.0 → %di=0.097% (≤2.0%). Todas cumplen → conclusión global “Cumple”.

  {
    "soluciones": [
      {
        "solucion": "[Solucion Estandar X]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 250000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 249800.0 },
              { "replica": 2, "area": 250100.0 },
              { "replica": 3, "area": 250100.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Sample Stability Time 1",
            "promedio_areas": 249667.0,
            "diferencia_promedios": 0.133,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 249300.0 },
              { "replica": 2, "area": 249900.0 },
              { "replica": 3, "area": 249800.0 }
            ]
          }
        ]
      },
      {
        "solucion": "[Solucion Muestra Y]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 310000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 309600.0 },
              { "replica": 2, "area": 310100.0 },
              { "replica": 3, "area": 310300.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Sample Stability Time 1",
            "promedio_areas": 309700.0,
            "diferencia_promedios": 0.097,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 309500.0 },
              { "replica": 2, "area": 309800.0 },
              { "replica": 3, "area": 309800.0 }
            ]
          }
        ]
      }
    ],
    "referencia_analitica": ["[HT00XXXXXX]", "[METODO-REF-YY]"],
    "conclusion_estabilidad_muestra": "Cumple"
  }

  - Ejemplo B (caso con incumplimiento, opcional para pruebas) — Razonamiento (resumen): C2 t2 %di=2.7% (>2.0%) → “No Cumple” para esa entrada; al existir alguna entrada “No Cumple”, la conclusión global de la solución (o del lote completo si así se define) es “No Cumple”.

  — RESTRICCIÓN CRÍTICA (repetir siempre): **RAZONAMIENTO → LUEGO SALIDA**. Cualquier cálculo o inferencia (promedios, %di, reglas por condición/tiempo) debe documentarse antes de la salida final.
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
"""

RULES_SET_9 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Estas reglas aplican al structured_extraction_agent.

  - Objetivo: Extraer y estructurar datos de **estabilidad de soluciones de MUESTRA** desde reportes LIMS y protocolo, conforme a `Set9ExtractionModel`.

  - Plan iterativo (varios ciclos sobre el vectorstore):
    1) Descubrir soluciones de muestra: buscar tablas con tiempos (“Initial Sample Stability”, “Sample Stability Time 1..n”), réplicas (“Solucion Muestra R1..R3”) y **Condición 1/2**.
    2) Extracción por solución (subciclo por cada solución de muestra):
      • Construir `data_estabilidad_solucion` con entradas por (tiempo_estabilidad, condicion_estabilidad).  
      • Para cada entrada:
        - `data_condicion` ← lista de {replica:int, area:float} recolectada de R1..R3.  
        - `promedio_areas` ← si el LIMS lo reporta (p.ej. “Promedio Solucion Muestra Tiempo …”), guardarlo; si falta, usar "[pendiente_calcular]".  
        - `diferencia_promedios` ( %di ) ← si el LIMS lo reporta (“%di …”), guardarlo; si falta, "[pendiente_calcular]".  
        - `criterio_aceptacion` ← literal del Protocolo (umbral de variación vs. t0, p.ej. "|%di| <= 2.0%").  
        - `conclusion_estabilidad` ← inicializar "[pendiente_validar]".
    3) Trazabilidad obligatoria (interna): source_document (LIMS/Protocolo), page/span, query_used, confidence, cleaning_notes.
    4) Normalización mínima:
      • Decimales coma→punto; áreas/promedios como float.  
      • Mantener textos exactos para tiempos; `replica` entero ≥1.  
      • Eliminar filas sin área, anotando motivo.
    5) Deduplificar corridas: unificar por (solución, tiempo, condición, réplica, run_id) priorizando la más completa/reciente.
    6) Relleno de huecos: si tras los ciclos faltan campos, conservar "[pendiente_calcular]" o "[pendiente_validar]" y registrar en trazabilidad.

  - Ejemplo de extracción estructurada (Set9ExtractionModel con placeholders):
  {
    "soluciones": [
      {
        "solucion": "[Solucion Muestra A]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 305000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 304700.0 },
              { "replica": 2, "area": 305200.0 },
              { "replica": 3, "area": 305100.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Sample Stability Time 1",
            "promedio_areas": "[pendiente_calcular]",
            "diferencia_promedios": "[pendiente_calcular]",
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 304600.0 },
              { "replica": 2, "area": 304900.0 },
              { "replica": 3, "area": 305000.0 }
            ]
          }
        ]
      },
      {
        "solucion": "[Solucion Muestra B]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 2",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 298500.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "[pendiente_validar]",
            "data_condicion": [
              { "replica": 1, "area": 298300.0 },
              { "replica": 2, "area": 298600.0 },
              { "replica": 3, "area": 298600.0 }
            ]
          }
        ]
      }
    ],
    "referencia_analitica": ["[HT00XXXXXX]", "[METODO-REF-YY]"]
  }
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al reasoning_agent.

  - RESTRICCIÓN CRÍTICA: **El razonamiento SIEMPRE debe preceder a la conclusión/salida** y documentar cálculos/interferencias.

  - Pasos por solución de muestra (explicitar cálculos):
    1) Agrupar por (tiempo_estabilidad, condicion_estabilidad) y validar N réplicas (≥3); listar áreas usadas.
    2) Cálculos intermedios:
      • Si `promedio_areas` == "[pendiente_calcular]": promedio = mean(áreas).  
      • Para cada (tiempo, condición), calcular %di contra el **promedio del tiempo inicial de la MISMA condición**:  
        %di = 100 * abs(prom_t - prom_t0) / prom_t0.  
        Si `diferencia_promedios` está "[pendiente_calcular]", asignar el %di calculado.
    3) Comparación con criterio:
      • Parsear umbral desde `criterio_aceptacion` (p.ej. 2.0%).  
      • Si |%di| ≤ umbral → `conclusion_estabilidad` = "Cumple"; si no → "No Cumple".
    4) Documentar explícitamente: t0, promedios por tiempo, %di y umbral aplicado por condición.

  - Mini-ejemplo de razonamiento (orden correcto):
    • Condición 1 (t0): prom_t0 = 305000.0  
    • Condición 1 (t1): prom_t1 = 304833.3 → %di = 100*|304833.3-305000|/305000 = 0.055%  
    • Umbral = 2.0% → Cumple → fijar `conclusion_estabilidad`="Cumple".
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  Estas reglas aplican al supervisor.

  - Modelo de salida: `Set9StructuredOutputSupervisor`. **Emitir SOLO el JSON final** tras documentar el razonamiento.
  - Integración:
    • Completar `promedio_areas` y `diferencia_promedios` si fueron calculados.  
    • Establecer `conclusion_estabilidad` por cada (tiempo, condición).  
    • Mantener `referencia_analitica`.

  - Ejemplo de salida del supervisor — Orden: 1) razonamiento (resumen) → 2) JSON final
  Razonamiento (resumen): Para [Solucion Muestra A] C1: t0=305000.0; t1=304833.3 → %di=0.055% (≤2.0%) ⇒ Cumple. Para [Solucion Muestra B] C2: t0=298500.0 (sin otros tiempos) ⇒ por defecto Cumple en t0.

  {
    "soluciones": [
      {
        "solucion": "[Solucion Muestra A]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 305000.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 304700.0 },
              { "replica": 2, "area": 305200.0 },
              { "replica": 3, "area": 305100.0 }
            ]
          },
          {
            "condicion_estabilidad": "Condicion 1",
            "tiempo_estabilidad": "Sample Stability Time 1",
            "promedio_areas": 304833.3,
            "diferencia_promedios": 0.055,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 304600.0 },
              { "replica": 2, "area": 304900.0 },
              { "replica": 3, "area": 305000.0 }
            ]
          }
        ]
      },
      {
        "solucion": "[Solucion Muestra B]",
        "data_estabilidad_solucion": [
          {
            "condicion_estabilidad": "Condicion 2",
            "tiempo_estabilidad": "Initial Sample Stability",
            "promedio_areas": 298500.0,
            "diferencia_promedios": 0.0,
            "criterio_aceptacion": "[|%di| <= 2.0% vs tiempo inicial]",
            "conclusion_estabilidad": "Cumple",
            "data_condicion": [
              { "replica": 1, "area": 298300.0 },
              { "replica": 2, "area": 298600.0 },
              { "replica": 3, "area": 298600.0 }
            ]
          }
        ]
      }
    ],
    "referencia_analitica": ["[HT00XXXXXX]", "[METODO-REF-YY]"]
  }

  — Recordatorio estricto: **RAZONAMIENTO → LUEGO SALIDA**. Cualquier cálculo (promedios, %di, parsing del umbral) debe consignarse antes del JSON final.
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
"""


RULES_SET_10 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Aplica al structured_extraction_agent.

  - Objetivo: Extraer y estructurar datos de **estabilidad de la fase móvil** por ingrediente activo (API) desde hojas de trabajo/protocolos LIMS, siguiendo `Set10ExtractionModel`.

  - Plan iterativo (varios ciclos sobre el vectorstore):
    1) Identificar APIs: buscar en “DESARROLLO DEL PROCEDIMIENTO” y tablas de “Estabilidad Fase Movil Tiempo inicial/1/2…”.
    2) Por API y por tiempo (tiempo inicial, 1, 2…):
      • Recolectar réplicas (N°→`replica`) con: Area→`areas_system`, Tiempo de retención→`tiempo_retencion`, USP tailing→`usp_tailing`, Resolución→`resolucion`, Exactitud→`exactitud`.
      • Extraer si existen los agregados del tiempo: `promedio_areas_system`, `promedio_tiempo_retencion`, `promedio_usp_tailing`, `promedio_resolucion`, `rsd_areas_system`.
      • Extraer `criterio_aceptacion` literal (ej.: “RSD ≤ 2.0%; ΔRt ≤ 2.0% vs t0; USP tailing ≤ 2.0”).
      • Inicializar conclusiones: `conclusion_areas_system`, `conclusion_tiempo_retencion`, `conclusion_usp_tailing` = "[pendiente_validar]".
    3) Trazabilidad mínima (interna): source_document (LIMS/Protocolo), página/span, query usada, notas de limpieza (coma→punto, unidades removidas).
    4) Normalización:
      • Números a float; `replica` entero ≥1; conservar texto exacto de `tiempo`.
      • Omitir filas sin área o métricas clave, anotando motivo en trazabilidad.
    5) Dedupe: unificar por (api, tiempo, replica) priorizando corrida más completa/reciente.
    6) Huecos: si faltan agregados, usar "[pendiente_calcular]" y registrar.

  - Ejemplo de extracción (placeholders válidos):
  {
    "activos_fase_movil": [
      {
        "nombre": "[API_1]",
        "data_fase_movil_tiempos": [
          {
            "tiempo": "Estabilidad Fase Movil Tiempo inicial",
            "promedio_areas_system": 520000.0,
            "promedio_tiempo_retencion": 6.20,
            "promedio_usp_tailing": 1.25,
            "promedio_resolucion": 2.10,
            "rsd_areas_system": 0.85,
            "criterio_aceptacion": "[RSD ≤ 2.0%; ΔRt ≤ 2.0% vs t0; USP tailing ≤ 2.0]",
            "conclusion_areas_system": "[pendiente_validar]",
            "conclusion_tiempo_retencion": "[pendiente_validar]",
            "conclusion_usp_tailing": "[pendiente_validar]",
            "data_fase_movil_tiempo": [
              { "replica": 1, "areas_system": 519500.0, "tiempo_retencion": 6.18, "usp_tailing": 1.24, "resolucion": 2.08, "exactitud": 99.7 },
              { "replica": 2, "areas_system": 520300.0, "tiempo_retencion": 6.21, "usp_tailing": 1.26, "resolucion": 2.12, "exactitud": 100.1 },
              { "replica": 3, "areas_system": 520200.0, "tiempo_retencion": 6.21, "usp_tailing": 1.25, "resolucion": 2.10, "exactitud": 100.0 }
            ]
          },
          {
            "tiempo": "Estabilidad Fase Movil Tiempo 1",
            "promedio_areas_system": "[pendiente_calcular]",
            "promedio_tiempo_retencion": "[pendiente_calcular]",
            "promedio_usp_tailing": "[pendiente_calcular]",
            "promedio_resolucion": "[pendiente_calcular]",
            "rsd_areas_system": "[pendiente_calcular]",
            "criterio_aceptacion": "[RSD ≤ 2.0%; ΔRt ≤ 2.0% vs t0; USP tailing ≤ 2.0]",
            "conclusion_areas_system": "[pendiente_validar]",
            "conclusion_tiempo_retencion": "[pendiente_validar]",
            "conclusion_usp_tailing": "[pendiente_validar]",
            "data_fase_movil_tiempo": [
              { "replica": 1, "areas_system": 520400.0, "tiempo_retencion": 6.19, "usp_tailing": 1.27, "resolucion": 2.05, "exactitud": 99.8 },
              { "replica": 2, "areas_system": 520600.0, "tiempo_retencion": 6.20, "usp_tailing": 1.26, "resolucion": 2.09, "exactitud": 100.0 },
              { "replica": 3, "areas_system": 520300.0, "tiempo_retencion": 6.20, "usp_tailing": 1.25, "resolucion": 2.07, "exactitud": 99.9 }
            ]
          }
        ]
      }
    ],
    "referencia_estabilidad_fase_movil": "[HT00XXXXXX/REF]"
  }
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  Aplica al reasoning_agent. **El razonamiento SIEMPRE precede a la conclusión/salida. Documentar cálculos/interferencias.**

  - Cálculos intermedios por API y por tiempo:
    1) Si algún promedio o `rsd_areas_system` = "[pendiente_calcular]":
      • promedio = mean(valores).  
      • rsd% = 100 * std_muestral(valores) / mean(valores).
      • promedio_tiempo_retencion/promedio_usp_tailing/promedio_resolucion: media de sus réplicas.
    2) Definir baseline t0: métricas del “Tiempo inicial”.
      • ΔRt% (tiempo t) = 100 * |prom_rt_t - prom_rt_t0| / prom_rt_t0.
    3) Parsear `criterio_aceptacion`:
      • Extraer límites numéricos: e.g., rsd_max, drt_max, tailing_max.  
      • Si faltan en documentos, usar defaults cautelares marcando `criterio_inferido=true`: rsd_max=2.0, drt_max=2.0, tailing_max=2.0.
    4) Verificación individual (explicar breve):
      • Áreas del sistema: rsd% ≤ rsd_max → “Cumple”, si no “No Cumple”.  
      • Tiempo de retención: ΔRt% ≤ drt_max → “Cumple”, si no “No Cumple”.  
      • USP tailing: promedio_usp_tailing ≤ tailing_max → “Cumple”, si no “No Cumple”.
    5) Registrar explícitamente: valores usados (t0, promedios, rsd, ΔRt%, límites) antes de fijar las conclusiones.

  - Mini-ejemplo (orden correcto):
    • t0: prom_areas=520000.0, rsd=0.85%; prom_rt=6.20; prom_tail=1.25.  
    • t1: prom_areas=520433.3, rsd=0.31%; prom_rt=6.20 → ΔRt%=0.00%; prom_tail=1.26.  
    • Criterio: RSD≤2.0; ΔRt%≤2.0; tailing≤2.0 ⇒ todo Cumple.
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  Aplica al supervisor.

  - Modelo de salida: `Set10StructuredOutputSupervisor`.  
  - Integración:
    • Rellenar promedios/RSD calculados; fijar `conclusion_areas_system`, `conclusion_tiempo_retencion`, `conclusion_usp_tailing`.  
    • Mantener `referencia_estabilidad_fase_movil`.  
    • **La salida final debe ser SOLO JSON bien formado** (el razonamiento queda documentado antes).

  - Ejemplo (resumen de razonamiento → luego JSON final):
  Razonamiento (resumen): [API_1] t0: rsd=0.85% (≤2.0) Cumple; t1: rsd=0.31% (≤2.0) Cumple. ΔRt%(t1 vs t0)=0.00% (≤2.0) Cumple. USP tailing promedio t1=1.26 (≤2.0) Cumple.

  {
    "activos_fase_movil": [
      {
        "nombre": "[API_1]",
        "data_fase_movil_tiempos": [
          {
            "tiempo": "Estabilidad Fase Movil Tiempo inicial",
            "promedio_areas_system": 520000.0,
            "promedio_tiempo_retencion": 6.20,
            "promedio_usp_tailing": 1.25,
            "promedio_resolucion": 2.10,
            "rsd_areas_system": 0.85,
            "criterio_aceptacion": "[RSD ≤ 2.0%; ΔRt ≤ 2.0% vs t0; USP tailing ≤ 2.0]",
            "conclusion_areas_system": "Cumple",
            "conclusion_tiempo_retencion": "Cumple",
            "conclusion_usp_tailing": "Cumple",
            "data_fase_movil_tiempo": [
              { "replica": 1, "areas_system": 519500.0, "tiempo_retencion": 6.18, "usp_tailing": 1.24, "resolucion": 2.08, "exactitud": 99.7 },
              { "replica": 2, "areas_system": 520300.0, "tiempo_retencion": 6.21, "usp_tailing": 1.26, "resolucion": 2.12, "exactitud": 100.1 },
              { "replica": 3, "areas_system": 520200.0, "tiempo_retencion": 6.21, "usp_tailing": 1.25, "resolucion": 2.10, "exactitud": 100.0 }
            ]
          },
          {
            "tiempo": "Estabilidad Fase Movil Tiempo 1",
            "promedio_areas_system": 520433.3,
            "promedio_tiempo_retencion": 6.20,
            "promedio_usp_tailing": 1.26,
            "promedio_resolucion": 2.07,
            "rsd_areas_system": 0.31,
            "criterio_aceptacion": "[RSD ≤ 2.0%; ΔRt ≤ 2.0% vs t0; USP tailing ≤ 2.0]",
            "conclusion_areas_system": "Cumple",
            "conclusion_tiempo_retencion": "Cumple",
            "conclusion_usp_tailing": "Cumple",
            "data_fase_movil_tiempo": [
              { "replica": 1, "areas_system": 520400.0, "tiempo_retencion": 6.19, "usp_tailing": 1.27, "resolucion": 2.05, "exactitud": 99.8 },
              { "replica": 2, "areas_system": 520600.0, "tiempo_retencion": 6.20, "usp_tailing": 1.26, "resolucion": 2.09, "exactitud": 100.0 },
              { "replica": 3, "areas_system": 520300.0, "tiempo_retencion": 6.20, "usp_tailing": 1.25, "resolucion": 2.07, "exactitud": 99.9 }
            ]
          }
        ]
      }
    ],
    "referencia_estabilidad_fase_movil": "[HT00XXXXXX/REF]"
  }

  — Recordatorio estricto: **RAZONAMIENTO → LUEGO SALIDA**. Cualquier cálculo (promedios, RSD, ΔRt%, parsing de umbrales) DEBE constar antes del JSON final.
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
"""


RULES_SET_11 = """
  <REGLAS_DE_EXTRACCION_ESTRUCTURADA>
  Aplica al structured_extraction_agent.

  - Objetivo: Extraer y estructurar datos de **robustez** por ingrediente activo (API) desde Protocolo/RA/LIMS, siguiendo `Set11ExtractionModel`.

  - Plan iterativo (varios ciclos sobre el/los vectorstore):
    1) Protocolo de validación → Tabla “Condiciones de robustez”: poblar `experimento_robustez` como `DataFactoresExperimentos`
      • Campos: nombre_experimento, temperatura, flujo, volumen_inyeccion, fase_movil.
    2) Reporte LIMS / Reporte Analítico → Bloques “Robustness Flow/Temperature/Injection volume/Mobile phase”
      • Por condición (Nominal, Baja, Alta, …) y réplica (1..n) crear `DataRobustezStrOutput`:
        - experimento (texto exacto; ej. "Robustness Flow – Bajo"),
        - replica (int ≥1),
        - valores_aproximados (%, sin símbolo),
        - promedio_experimento = valor reportado o "[pendiente_calcular]",
        - diferencia_porcentaje = %di vs condición nominal o "[pendiente_calcular]".
    3) Referencias/criterios:
      • `referencia_robustez` (p. ej., "<USP <capítulo>> / SOP-[ID]").
      • `criterio_robustez` (lista de `criterios`; si el doc da límites, tomarlos literal).
    4) Normalización:
      • Punto decimal ".", quitar "%", trim/colapso de espacios; conservar mayúsculas/tildes.
    5) Trazabilidad mínima (interna): source_document, sección/página, query, notas de limpieza.
    6) Dedupe por (API, experimento, réplica) priorizando corridas más completas/recientes.
    7) Huecos: si faltan promedios/%di → marcar "[pendiente_calcular]" y resolver en RAZONAMIENTO.

  - Ejemplo de extracción (placeholders válidos):
  {
    "activos_robustez": [
      {
        "nombre": "[API_1]",
        "robustez": [
          { "experimento": "Robustness Flow – Nominal", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
          { "experimento": "Robustness Flow – Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
          { "experimento": "Robustness Flow – Bajo",    "replica": 1, "valores_aproximados": 99.6,  "promedio_experimento": "[pendiente_calcular]", "diferencia_porcentaje": "[pendiente_calcular]" },
          { "experimento": "Robustness Flow – Alto",    "replica": 1, "valores_aproximados": 100.7, "promedio_experimento": "[pendiente_calcular]", "diferencia_porcentaje": "[pendiente_calcular]" },
          { "experimento": "Robustness Temperature – Nominal", "replica": 1, "valores_aproximados": 100.3, "promedio_experimento": 100.3, "diferencia_porcentaje": 0.0 }
        ],
        "conclusion_robustez": "[por_definir_en_razonamiento]",
        "criterio_robustez": ["[CRITERIO_RANGO_%DI]", "[CRITERIO_ADICIONAL]"]
      }
    ],
    "referencia_robustez": "[REFERENCIA_ANALITICA_ROBUSTEZ]",
    "experimento_robustez": [
      { "nombre_experimento": "Flow",      "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
      { "nombre_experimento": "Flow-Bajo", "temperatura": 30.0, "flujo": 0.90, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
      { "nombre_experimento": "Flow-Alto", "temperatura": 30.0, "flujo": 1.10, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" }
    ]
  }
  </REGLAS_DE_EXTRACCION_ESTRUCTURADA>

  <REGLAS_DE_RAZONAMIENTO>
  Aplica al reasoning_agent. **El razonamiento SIEMPRE precede a la conclusión/salida. Documentar cálculos/inferencias.**

  - Pasos intermedios por API y por factor:
    1) Agrupar por experimento-condición (Nominal/Bajo/Alto…). Si `promedio_experimento="[pendiente_calcular]"`, calcular:
      • promedio_experimento = mean(valores_aproximados de esa condición).
    2) Identificar baseline nominal del mismo factor:
      • promedio_nominal = promedio_experimento de condición Nominal.
      • %di = 100 * (promedio_experimento - promedio_nominal) / promedio_nominal.
    3) Parsear `criterio_robustez`:
      • Extraer umbral |%di| ≤ [UMBRAL_%]; si no existe en documentos, usar default cautelar 2.0 y anotar `criterio_inferido=true`.
    4) Verificación por condición (explicar breve):
      • Si |%di| ≤ umbral → “Cumple”, si no → “No Cumple”.
    5) Conclusión por API:
      • "Cumple" si todas las condiciones evaluadas cumplen; de lo contrario "No Cumple".
    6) Registrar explícitamente valores usados (prom_nominal, promedios, %di, umbral) antes de fijar la conclusión.

  - Mini-ejemplo (orden correcto):
    • Flow–Nominal: promedio=100.1.  
    • Flow–Bajo: promedio=99.6 → %di=-0.50%.  
    • Flow–Alto: promedio=100.7 → %di=+0.60%.  
    • Umbral |%di| ≤ 2.0% ⇒ todas “Cumple” → API “[API_1]” = “Cumple”.
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_ESTRUCTURADA>
  Aplica al supervisor.

  - Modelo de salida: `Set11StructuredOutputSupervisor`.  
  - Integración:
    • Reemplazar todos los "[pendiente_calcular]" por valores numéricos calculados.  
    • Establecer `conclusion_robustez` = "Cumple" | "No Cumple".  
    • Mantener `referencia_robustez` y mapear `experimento_robustez` → `experimentos_robustez`.  
  - **La salida final debe ser SOLO JSON bien formado** (el razonamiento va antes).

  - Ejemplo (resumen muy breve del razonamiento → luego JSON final):
  Razonamiento (resumen): [API_1] Flow: %di_bajo=-0.50%; %di_alto=+0.60% (≤2.0%) ⇒ Cumple.

  {
    "activos_robustez": [
      {
        "nombre": "[API_1]",
        "robustez": [
          { "experimento": "Robustness Flow – Nominal", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
          { "experimento": "Robustness Flow – Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
          { "experimento": "Robustness Flow – Bajo",    "replica": 1, "valores_aproximados": 99.6,  "promedio_experimento": 99.6, "diferencia_porcentaje": -0.50 },
          { "experimento": "Robustness Flow – Alto",    "replica": 1, "valores_aproximados": 100.7, "promedio_experimento": 100.7, "diferencia_porcentaje": 0.60 },
          { "experimento": "Robustness Temperature – Nominal", "replica": 1, "valores_aproximados": 100.3, "promedio_experimento": 100.3, "diferencia_porcentaje": 0.0 }
        ],
        "conclusion_robustez": "Cumple",
        "criterio_robustez": ["|%di| ≤ 2.0%"]
      }
    ],
    "referencia_robustez": "[REFERENCIA_ANALITICA_ROBUSTEZ]",
    "experimentos_robustez": [
      { "nombre_experimento": "Flow",      "temperatura": 30.0, "flujo": 1.00, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
      { "nombre_experimento": "Flow-Bajo", "temperatura": 30.0, "flujo": 0.90, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" },
      { "nombre_experimento": "Flow-Alto", "temperatura": 30.0, "flujo": 1.10, "volumen_inyeccion": 10.0, "fase_movil": "Buffer pH [x]:ACN [y]" }
    ]
  }

  — Recordatorio estricto: **RAZONAMIENTO → LUEGO SALIDA**. Cualquier cálculo (promedios, %di, parsing de umbrales) DEBE constar antes del JSON final.
  </REGLAS_DE_SALIDA_ESTRUCTURADA>
  """