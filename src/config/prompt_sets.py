RULES_SET_2 = """
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
  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Comparar sistemáticamente cada parámetro de regresión extraído contra su criterio de aceptación correspondiente para emitir una conclusión global sobre la linealidad del método, y generar las gráficas de regresión y residuales correspondientes.

    - **Entradas:** El objeto JSON completo poblado por el `structured_extraction_agent`. Solo tomarás la data extraida del reporte LIMS, y los criterios de linealidad del protocolo de validación. De esta forma procederás con los pasos del razonamiento.

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
  `<REGLAS_DE_RAZONAMIENTO>`
  Estas reglas aplican al `reasoning_agent`.

    - **Objetivo Principal:** Verificar si el porcentaje de recuperación promedio por cada nivel se encuentra dentro del criterio encontrado en el protocolo de validación.

    - **Entradas:** El objeto JSON completo del `structured_extraction_agent`.

    - **Pasos del Razonamiento (por cada API):**

      1.  **Agrupar y Promediar por Nivel:**
            - Agrupa los datos de `exactitud_metodo` por el campo `nivel`.
            - Para cada nivel, calcula el promedio de los valores de `recuperacion`. Usa la herramienta average_tool para calcular el promedio.
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
              { "nivel": "Level I", "recuperacion": "VALOR_RECUPERACION_1", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_1" },
              { "nivel": "Level I", "recuperacion": "VALOR_RECUPERACION_2", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_2" },
              { "nivel": "Level I", "recuperacion": "VALOR_RECUPERACION_3", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_3" },
              { "nivel": "Level II", "recuperacion": "VALOR_RECUPERACION_4", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_4" },
              { "nivel": "Level II", "recuperacion": "VALOR_RECUPERACION_5", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_5" },
              { "nivel": "Level II", "recuperacion": "VALOR_RECUPERACION_6", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_6" },
              { "nivel": "Level III", "recuperacion": "VALOR_RECUPERACION_7", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_7" },
              { "nivel": "Level III", "recuperacion": "VALOR_RECUPERACION_8", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_8" },
              { "nivel": "Level III", "recuperacion": "VALOR_RECUPERACION_9", "recuperacion_promedio": "VALOR_RECUPERACION_PROMEDIO_9" }
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
  - **Entradas:** Mensaje que contiene todo el contexto incluyendo un JSON generado por un agente de extracción.
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
  <REGLAS_DE_RAZONAMIENTO>
  Estas reglas aplican al `reasoning_agent`.

    - **Propósito:** Ubicar los datos ya estructurados en el modelo de salida `Set11StructuredOutputSupervisor` SIN realizar ningún cálculo, inferencia, validación numérica ni conclusión. Es exclusivamente un mapeo 1:1 de campos.
    - **Herramientas restringidas:** No utilices ninguna herramienta. No llames funciones externas. No apliques fórmulas ni redondeos.
    - **Entradas:** Objeto JSON producido por el `structured_extraction_agent` que incluye la clave `experimento_robustez` (lista de `DataFactoresExperimentos`).
    - **Convenciones para placeholders (solo en ejemplos):**
      - `<STR_X>`: cualquier texto.
      - `<NUM_X>`: cualquier número (usa el tipo que corresponda si implementas).
    - **Pasos del razonamiento (mapeo literal):**
      1. Verifica únicamente la presencia de la clave `experimento_robustez`. Si no existe, emite `experimentos_robustez: []` (lista vacía). No rellenes, no inventes.
      2. Copia los elementos de `experimento_robustez` a `experimentos_robustez` **sin alterar**:
        - No cambies valores, unidades, tipos, ni el orden.
        - No crees ni borres campos.
        - No transformes cadenas (no trims, no upper/lower).
        - Mantén `null` como `null` si viniera así.
      3. No calcules promedios, diferencias, ni porcentajes. No determines conclusiones. No modifiques criterios.
      4. No agregues narrativa ni comentarios en la salida. El resultado final debe ser exclusivamente el JSON del modelo de salida.
    - **Mini-ejemplo (mapeo 1:1, data-agnostic):**
      - **Entrada (extracto):**
        ```json
        {
          "experimento_robustez": [
            {
              "nombre_experimento": "<STR_EXPERIMENTO_A>",
              "temperatura": "<NUM_TEMPERATURA_A>",
              "flujo": "<NUM_FLUJO_A>",
              "volumen_inyeccion": "<NUM_VOL_INY_A>",
              "fase_movil": "<STR_FASE_A>"
            }
          ]
        }
        ```
      - **Salida esperada (renombrando la clave, sin cambios de contenido):**
        ```json
        {
          "experimentos_robustez": [
            {
              "nombre_experimento": "<STR_EXPERIMENTO_A>",
              "temperatura": "<NUM_TEMPERATURA_A>",
              "flujo": "<NUM_FLUJO_A>",
              "volumen_inyeccion": "<NUM_VOL_INY_A>",
              "fase_movil": "<STR_FASE_A>"
            }
          ]
        }
        ```
  </REGLAS_DE_RAZONAMIENTO>

  <REGLAS_DE_SALIDA_SUPERVISOR>
  Aplica al `supervisor_agent`.

    - **Modelo de salida obligatorio:** `Set11StructuredOutputSupervisor`.
    - **Formato:** ÚNICO objeto JSON bien formado; NO se permite texto adicional, comentarios, ni narrativa.
    - **Integración de datos (solo mapeo):**
      - Renombra la clave `experimento_robustez` → `experimentos_robustez`.
      - Copia **literalmente** cada objeto `DataFactoresExperimentos` sin alteraciones en sus campos:
        - `nombre_experimento`, `temperatura`, `flujo`, `volumen_inyeccion`, `fase_movil`.
      - No agregues otras claves a menos que estén definidas en el modelo. Para `Set11StructuredOutputSupervisor`, **solo** debe emitirse `experimentos_robustez`.
      - Si la entrada carece de `experimento_robustez`, devuelve `"experimentos_robustez": []`.
    - **Ejemplo de salida final del supervisor (data-agnostic):**
      ```json
      {
        "experimentos_robustez": [
          {
            "nombre_experimento": "<STR_EXPERIMENTO_A>",
            "temperatura": "<NUM_TEMPERATURA_A>",
            "flujo": "<NUM_FLUJO_A>",
            "volumen_inyeccion": "<NUM_VOL_INY_A>",
            "fase_movil": "<STR_FASE_A>"
          },
          {
            "nombre_experimento": "<STR_EXPERIMENTO_B>",
            "temperatura": "<NUM_TEMPERATURA_B>",
            "flujo": "<NUM_FLUJO_B>",
            "volumen_inyeccion": "<NUM_VOL_INY_B>",
            "fase_movil": "<STR_FASE_B>"
          },
          {
            "nombre_experimento": "<STR_EXPERIMENTO_C>",
            "temperatura": "<NUM_TEMPERATURA_C>",
            "flujo": "<NUM_FLUJO_C>",
            "volumen_inyeccion": "<NUM_VOL_INY_C>",
            "fase_movil": "<STR_FASE_C>"
          }
        ]
      }
      ```
    - **Recordatorio estricto:** No realices cálculos, comparaciones, imputaciones ni conclusiones. Emite **solo** el JSON del modelo con el mapeo literal.
  </REGLAS_DE_SALIDA_SUPERVISOR>
"""

RULES_SET_12 = """
  <REGLAS_DE_RAZONAMIENTO>
    Estas reglas aplican al `reasoning_agent`.

      - **Propósito:** Evaluar si cada **Entidad de Análisis** (`variable_entrada`) cumple los criterios de robustez del protocolo, comparando los resultados de las **Condiciones Modificadas** (Bajo y Alto) contra la **Condición Nominal** y preparando la salida para `Set12StructuredOutputSupervisor`.
      - **Herramientas restringidas:** No utilices `linealidad_tool`; está prohibida en este conjunto.
      - **Entradas:** Objeto JSON producido por el `structured_extraction_agent` (que sigue el modelo `Set12ExtractionModel`).
      - **Pasos del razonamiento:**
        1.  Agrupa las réplicas por **Entidad de Análisis** (`variable_entrada`) y por **Condición de Experimento** (Nominal, Bajo, Alto).
        2.  Calcula el `promedio_experimento` para cada `replicas` de cada condición si los valores del campo `promedio_experimento` en la salida se dejaron en `null`, documentando claramente el método de cálculo (i.e., promedio de las réplicas).
        3.  Para cada **Condición Modificada** (Bajo y Alto), calcula el **Porcentaje de Diferencia** (`diferencia_porcentaje` o `%di`) usando la fórmula:
            $$ \%di = 100 \times \frac{(\text{promedio\_condicion\_modificada} - \text{promedio\_nominal})}{\text{promedio\_nominal}} $$
            Registra este resultado antes de compararlo.
        4.  Compara cada `%di` (tanto `di_porcentaje_bajo` como `di_porcentaje_alto`) con el `criterio_robustez` literal. Si el criterio incluye otras verificaciones (ej. orden de elución, estabilidad), deja evidencia textual del chequeo.
        5.  Determina la `conclusion_robustez` por **Entidad de Análisis**: "Cumple" únicamente si **todas** las condiciones evaluadas satisfacen los límites del `criterio_robustez`; de lo contrario, "No Cumple".
        6.  Resume en la narrativa los valores clave para cada Entidad (promedio nominal, %di por condición, umbral aplicado) antes de emitir la conclusión.
        7.  Señala cualquier dato faltante o supuesto que pueda afectar la interpretación.
      - **Mini-ejemplo (orden recomendado, usando nombres genéricos):**
        - `[Componente_X] Factor_A - Condición_Bajo`: promedio_nominal=100.1; promedio_bajo=99.6; %di=-0.50% (<=2.0%) -> Cumple.
        - `[Componente_X] Factor_A - Condición_Alto`: %di=+0.60% (<=2.0%) -> Cumple.
        - `[Componente_Y] Factor_B - Variante_C`: %di=+0.50% (<=2.5%) -> Cumple. Conclusión global Componente_Y = "Cumple".
    </REGLAS_DE_RAZONAMIENTO>

    <br>

    <REGLAS_DE_SALIDA_SUPERVISOR>
    Aplica al `supervisor_agent`.

      - **Modelo de salida obligatorio:** `Set12StructuredOutputSupervisor`.
      - **Formato:** único objeto JSON bien formado; no se permite texto adicional tras el razonamiento.
      - **Integración de datos:**
        - Copia las réplicas de `robustez` incorporando los valores calculados definitivos (`promedio_experimento` y `diferencia_porcentaje`).
        - El campo `experimento` en `DataRobustezStrOutput` debe crearse combinando la `variable_entrada` y la condición (ej: "Robustez [variable_entrada] - [Condición]").
        - El campo `nombre` en `ActivoRobustezStrOutput` representa el **Ingrediente Activo/Componente Principal** evaluado y debe ser genérico (ej: "[Componente_1]", "[Componente_2]").
        - Actualiza `conclusion_robustez` y `criterio_robustez` por **Entidad de Análisis** según el análisis.
        - Mantén `referencia_robustez` literal.
      - **Ejemplo de salida final del supervisor (utilizando placeholders):**
        ```json
        {
          "activos_robustez": [
            {
              "nombre": "[Componente_A]",
              "robustez": [
                { "experimento": "Robustez Factor_X - Nominal", "replica": 1, "valores_aproximados": 100.2, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
                { "experimento": "Robustez Factor_X - Nominal", "replica": 2, "valores_aproximados": 100.0, "promedio_experimento": 100.1, "diferencia_porcentaje": 0.0 },
                { "experimento": "Robustez Factor_X - Bajo", "replica": 1, "valores_aproximados": 99.6, "promedio_experimento": 99.6, "diferencia_porcentaje": -0.50 },
                { "experimento": "Robustez Factor_X - Alto", "replica": 1, "valores_aproximados": 100.7, "promedio_experimento": 100.7, "diferencia_porcentaje": 0.60 }
              ],
              "conclusion_robustez": "Cumple",
              "criterio_robustez": "Aceptar si |%di| <= 2.0% para todas las condiciones."
            },
            {
              "nombre": "[Componente_B]",
              "robustez": [
                { "experimento": "Robustez Factor_Y - Nominal", "replica": 1, "valores_aproximados": 99.8, "promedio_experimento": 99.9, "diferencia_porcentaje": 0.0 },
                { "experimento": "Robustez Factor_Y - Bajo", "replica": 1, "valores_aproximados": 99.4, "promedio_experimento": 99.5, "diferencia_porcentaje": -0.40 }
              ],
              "conclusion_robustez": "Cumple",
              "criterio_robustez": "Aceptar si |%di| <= 2.5% para cada condición de robustez."
            }
          ],
          "referencia_robustez": "[REFERENCIA_DOCUMENTAL_GENÉRICA]"
          // El campo 'experimentos_robustez' fue omitido en este ejemplo, asume que debe incluirse según el modelo 'Set12StructuredOutputSupervisor' si el agente de extracción lo proporciona.
        }
        ```
      - **Recordatorio estricto:** El razonamiento debe documentar cálculos, umbrales y conclusiones antes de presentar el JSON final.
    </REGLAS_DE_SALIDA_SUPERVISOR>
"""