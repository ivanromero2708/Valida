RULES_SET_1 = """
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al agente de extracción estructurada (`structured_extraction_agent`).

  - Objetivo: Extraer la información del informe/protocolo de validación y documentos relacionados (Informe, Protocolo de Validación, RA, CoA, DMF) y estructurarla según el modelo `Set1ExtractionModel`.

  - Plan de Acción Iterativo (varios ciclos sobre el `vectorstore`):
    1. Localizar secciones base: portada del Informe, encabezado del Protocolo, tablas de Criterios de Aceptación y Parámetros de Validación, y secciones de APIs/activos (RA/CoA).
    2. Extracción por campo (un subciclo por cada campo del modelo):
       * Consulta 1 (Metadatos del Informe): validacion, codigo_informe.
       * Consulta 2 (Producto/Activos): nombre_producto, codigo_producto, lista_activos (cada API con nombre, concentracion).
       * Consulta 3 (Protocolo): código_protocolo_validacion, nombre_del_protocolo_validacion.
       * Consulta 4 (Alcance): concentracion_activos (resumen textual coherente con lista_activos), rango_validado.
       * Consulta 5 (Criterios): ctiterio_aceptacion (un objeto con todos los subcampos de criterios).
       * Consulta 6 (Parámetros): parámetros_validacion (un objeto con todos los subcampos de parámetros).
    3. Trazabilidad: cada valor extraído debe registrar source_document (Informe/Protocolo/RA/CoA/DMF), page_or_span, query_used, confidence y cleaning_notes si hubo normalización.
    4. Normalización mínima: trim/colapso de espacios; preservar mayúsculas/acentos; no inventar elementos.
    5. Relleno de huecos: si tras los ciclos no hay evidencia suficiente, usar [pendiente_validar] y registrar la razón en trazabilidad.

  - Ejemplo de Extracción Estructurada:
    {
      "validacion": "[nombre_del_informe]",
      "codigo_informe": "[codigo_del_informe]",
      "nombre_producto": "[nombre_producto]",
      "codigo_producto": "[codigo_producto]",
      "lista_activos": [
        { "nombre": "[api_1_nombre]", "concentracion": "[api_1_concentracion]" },
        { "nombre": "[api_2_nombre]", "concentracion": "[api_2_concentracion]" }
      ],
      "código_protocolo_validacion": "[pro-i&d-0404-version_00]",
      "nombre_del_protocolo_validacion": "[titulo_completo_del_protocolo]",
      "concentracion_activos": "[api_1 x mg + api_2 y mg]",
      "rango_validado": "[80%-120%]",
      "ctiterio_aceptacion": [
        {
          "criterio_selectividad": "[crit_selectividad]",
          "criterio_linealidad": "[crit_linealidad]",
          "criterio_exactitud": "[crit_exactitud]",
          "criterio_precision_sistema": "[crit_precision_sistema]",
          "criterio_precision_metodo": "[crit_precision_metodo]",
          "criterio_precision_intermedia": "[crit_precision_intermedia]",
          "criterio_rango": "[crit_rango]",
          "criterio_estabilidad_soluciones": "[crit_estabilidad_soluciones]",
          "criterio_estabilidad_fase_movil": "[crit_estabilidad_fase_movil]",
          "criterio_robustez": "[crit_robustez]"
        }
      ],
      "parámetros_validacion": [
        {
          "nombre": "[plan_parametros]",
          "selectividad": "[def_selectividad]",
          "linealidad": "[def_linealidad]",
          "exactitud": "[def_exactitud]",
          "precision_sistema": "[def_precision_sistema]",
          "precision_metodo": "[def_precision_metodo]",
          "precision_intermedia": "[def_precision_intermedia]",
          "rango": "[def_rango]",
          "estabilidad_soluciones": "[def_estabilidad_soluciones]",
          "estabilidad_fase_movil": "[def_estabilidad_fase_movil]",
          "robustez": "[def_robustez]"
        }
      ]
    }
</REGLAS_DE_EXTRACCION_ESTRUCTURADA>


<REGLAS_DE_RAZONAMIENTO>
Estas reglas aplican al agente de razonamiento (`reasoning_agent`).

  - Regla Principal: Consolidar y validar cada campo de Set1ExtractionModel comparando entre fuentes (prioridad sugerida: Protocolo > Informe > RA > CoA > DMF) antes de decidir el valor final.
  - Orden Estricto: el razonamiento SIEMPRE precede a la conclusión/salida. Documentar pasos, evidencias y cualquier inferencia intermedia.

  - Pasos del Razonamiento:
    1. Consolidación por campo: para cada campo, listar valores candidatos por fuente y elegir el más preciso/reciente/completo explicando la decisión.
    2. Consistencia: verificar que concentracion_activos sea coherente con lista_activos; explicar si hubo resumen/normalización.
    3. Parámetros y Criterios: confirmar que los subcampos de parámetros_validacion y ctiterio_aceptacion provienen de la tabla del Protocolo (o fuente equivalente) con páginas.
    4. Inferencias: si un texto se compone de varias secciones (título + subtítulo), documentar la inferencia previa a la decisión final.
    5. Bitácora breve: [(campo) -> (fuente/página) -> (valor adoptado) -> (motivo)].

  - Ejemplo de Razonamiento Detallado:
      - código_protocolo_validacion: Protocolo p.1 = "pro-i&d-0404-version 00" (adoptado por ser encabezado oficial).
      - nombre_del_protocolo_validacion: Protocolo p.1–2 = "[titulo_completo]" (más completo que abreviatura del Informe).
      - lista_activos vs concentracion_activos: RA tabla 3 y Protocolo p.3 coinciden; se resume como "api_1 x mg + api_2 y mg".
      - parámetros_validacion y ctiterio_aceptacion: Protocolo p.5–6, copiados con normalización mínima.
</REGLAS_DE_RAZONAMIENTO>


<REGLAS_DE_SALIDA_SUPERVISOR>
Estas reglas aplican al supervisor para la salida final.

  - Modelo de Salida: Un JSON bien formado que siga estrictamente `Set1StructuredOutputSupervisor`. No incluyas texto adicional ni bloques fuera del JSON.
  - Integración de Datos: La salida refleja los valores consolidados tras el razonamiento (sin bitácora).
  - Restricción Clave: La salida solo puede emitirse cuando el razonamiento documentado la precede.

  - Ejemplo de Salida del Supervisor:
    {
      "validacion": "[nombre_del_informe]",
      "codigo_informe": "[codigo_del_informe]",
      "nombre_producto": "[nombre_producto]",
      "codigo_producto": "[codigo_producto]",
      "lista_activos": [
        { "nombre": "[api_1_nombre]", "concentracion": "[api_1_concentracion]" },
        { "nombre": "[api_2_nombre]", "concentracion": "[api_2_concentracion]" }
      ],
      "código_protocolo_validacion": "[pro-i&d-0404-version_00]",
      "nombre_del_protocolo_validacion": "[titulo_completo_del_protocolo]",
      "concentracion_activos": "[api_1 x mg + api_2 y mg]",
      "rango_validado": "[80%-120%]",
      "ctiterio_aceptacion": [
        {
          "criterio_selectividad": "[crit_selectividad]",
          "criterio_linealidad": "[crit_linealidad]",
          "criterio_exactitud": "[crit_exactitud]",
          "criterio_precision_sistema": "[crit_precision_sistema]",
          "criterio_precision_metodo": "[crit_precision_metodo]",
          "criterio_precision_intermedia": "[crit_precision_intermedia]",
          "criterio_rango": "[crit_rango]",
          "criterio_estabilidad_soluciones": "[crit_estabilidad_soluciones]",
          "criterio_estabilidad_fase_movil": "[crit_estabilidad_fase_movil]",
          "criterio_robustez": "[crit_robustez]"
        }
      ],
      "parámetros_validacion": [
        {
          "nombre": "[plan_parametros]",
          "selectividad": "[def_selectividad]",
          "linealidad": "[def_linealidad]",
          "exactitud": "[def_exactitud]",
          "precision_sistema": "[def_precision_sistema]",
          "precision_metodo": "[def_precision_metodo]",
          "precision_intermedia": "[def_precision_intermedia]",
          "rango": "[def_rango]",
          "estabilidad_soluciones": "[def_estabilidad_soluciones]",
          "estabilidad_fase_movil": "[def_estabilidad_fase_movil]",
          "robustez": "[def_robustez]"
        }
      ]
    }
</REGLAS_DE_SALIDA_SUPERVISOR>
"""

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
          - `estandar_utilizados_protocolo`: ["[API\_Principal\_Estándar\_Farmacopea]", "[API\_Secundario\_Estándar\_de\_Trabajo]"]
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
Estas reglas aplican al agente de razonamiento (`reasoning_agent`).

  - **Regla Principal:** El razonamiento documentado **SIEMPRE** debe preceder a la generación de la salida final. El objetivo es reconciliar los nombres de las muestras, estandares, materiales, reactivos y columnas del protocolo con la ejecución documentada en las hojas de trabajo y/o las bitacoras.

  - **Pasos del Proceso de Razonamiento:**

    1.  **Reconciliación por Categoría:** Para cada tipo de ítem (columnas, equipos, reactivos, etc.), compara la lista extraída del protocolo (`*_utilizados_protocolo`) con la lista detallada de las hojas de trabajo (`*_utilizados`).

    2.  **Verificación de Conformidad y Coherencia:**

          - **Equipos:** Vas a tener incoherencias en la información extraida de las hojas de trabajo y bitacoras.. Por lo tanto asignarás aquí el nombre extraído de los equipos del protocolo por similaridad.
          - **Reactivos y Estándares:** Vas a tener incoherencias en la información extraida de las hojas de trabajo y bitacoras.. Por lo tanto asignarás aquí el nombre extraído de los equipos del protocolo por similaridad.
          - **Columnas:** Vas a tener incoherencias en la información extraida de las hojas de trabajo y bitacoras.. Por lo tanto asignarás aquí el nombre extraído de los equipos del protocolo por similaridad.
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
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al agente de extracción estructurada (`structured_extraction_agent`).

  - **Objetivo**: Extraer los datos de validación para el parámetro de **linealidad** de cada ingrediente activo (API) a partir de los documentos proporcionados (reportes LIMS, protocolos de validación) y estructurarlos según el modelo `Set3ExtractionModel`. NECESITO QUE EXTRAIGAS TODOS LOS DATOS DE RÉPLICAS Y REPETICIONES DEL PARÁMETRO DE VALIDACIÓN LINEALIDAD

  - **Plan de Acción Iterativo**:

    1.  **Identificar APIs**: Primero, realiza una consulta al `vectorstore` para listar todos los ingredientes activos que tienen datos de linealidad en los reportes LIMS.
    2.  **Extracción por API**: Para cada ingrediente activo identificado, ejecuta un ciclo de consultas enfocadas para poblar el modelo `ParametroLinealidadExtraccion`:
          * **Consulta 1 (Tabla de Linealidad)**: Extrae los datos tabulares de linealidad del sistema (`linealidad_sistema`).
          * **Consulta 2 (Parámetros de Regresión)**: Extrae los valores individuales como `rsd_factor`, `pendiente`, `intercepto`, `r`, `r2` y `porcentaje_intercepto`.
          * **Consulta 3 (Criterios de Aceptación)**: Extrae los `criterio_linealidad` del protocolo de validación.
          * **Consulta 4 (Referencias)**: Localiza y extrae los códigos de referencia (`referencia_linealidad`) asociados a los datos brutos.
    3.  **Trazabilidad**: Asegúrate de que cada pieza de información extraída mantenga una referencia a su documento de origen (ej. "Reporte LIMS", "Protocolo de Validación").

  - **Ejemplo de Extracción Estructurada**:
    * NOTA: EN LOS EJEMPLOS SOLO HAY UNA RÉPLICA, PERO NECESITO QUE EXTRAIGAS TODOS LOS DATOS DE RÉPLICAS Y REPETICIONES DEL PARÁMETRO DE VALIDACIÓN LINEALIDAD
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
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al `structured_extraction_agent`.

- Objetivo: Extraer la información de **exactitud** por API desde reportes LIMS (datos crudos) y protocolos (criterios) y estructurarla según `Set4ExtractionModel` (lista de `ActivoExactitudStrExt`).

- Plan de acción iterativo (varios ciclos sobre el vectorstore):
  1) Descubrimiento de APIs con exactitud: buscar en LIMS patrones tipo "Accuracy/Accurracy Solution_Level I/II/III".
  2) Extracción por API (un subciclo por API):
     • Datos crudos → poblar `exactitud_metodo` como lista de `DatosExactitudStrExt` con {nivel, recuperacion}.  
     • Criterios → extraer `criterio_exactitud` desde Protocolo (tabla de criterios).  
     • Referencia → localizar `referencia_exactitud` (código/ID del reporte LIMS o referencia analítica).
  3) Trazabilidad obligatoria (ledger interno): source_document (LIMS/Protocolo), page_or_span, query_used, confidence, cleaning_notes.
  4) Normalización mínima:
     • `nivel`: normalizar etiquetas (p. ej., "Level I/II/III"), conservando texto original si se requiere.  
     • `recuperacion`: convertir a float (unificar "," a "."); rango esperado 0–200.  
  5) Relleno de huecos: si falta evidencia tras los ciclos, marcar "[pendiente_validar]" y registrar la causa en trazabilidad.

- Ejemplo de extracción (Set4ExtractionModel con placeholders):
{
  "activos_exactitud": [
    {
      "nombre": "[api_1_nombre]",
      "exactitud_metodo": [
        { "nivel": "Level I", "recuperacion": 99.2 },
        { "nivel": "Level I", "recuperacion": 100.3 },
        { "nivel": "Level II", "recuperacion": 100.1 },
        { "nivel": "Level III", "recuperacion": 98.7 }
      ],
      "conclusion_exactitud": "[pendiente_validar]",
      "criterio_exactitud": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[rango_por_nivel_ej: 98.0–102.0%]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
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
Estas reglas aplican al `reasoning_agent`.

- Regla principal (innegociable): documentar razonamiento ANTES de cualquier conclusión/salida.
- Pasos mínimos por API:
  1) Agrupar por `nivel` y calcular `promedio_nivel = mean(recuperacion)` (documentar fórmula/valores usados).
  2) Comparar cada `promedio_nivel` contra el `criterio_exactitud` (p. ej., 98.0–102.0%). Registrar Cumple/No Cumple por nivel con breve justificación.
  3) Conclusión global `conclusion_exactitud`: si todos los niveles cumplen → "Cumple", si alguno falla → "No Cumple".
  4) Preparar datos para supervisor: para cada nivel emitir `{nivel, recuperacion=promedio_nivel, promedio=promedio_nivel}` y conservar `criterio_exactitud`. Incluir `referencia_exactitud`.

- Ejemplo de razonamiento (orden correcto):
  • Level I: valores [99.2, 100.3] → promedio 99.75% ∈ [98.0, 102.0] → Cumple.  
  • Level II: [100.1] → 100.1% ∈ rango → Cumple.  
  • Level III: [98.7] → 98.7% ∈ rango → Cumple.  
  • Conclusión global API [api_1_nombre]: "Cumple" (todos los niveles dentro de rango).
</REGLAS_DE_RAZONAMIENTO>

<REGLAS_DE_SALIDA_ESTRUCTURADA>
Estas reglas aplican al `supervisor`.

- Modelo de salida: `Set4StructuredOutputSupervisor` en JSON bien formado. **Solo** el JSON final (sin texto extra).
- Condición: emitir salida únicamente después de que el razonamiento esté documentado.
- Integración: transformar la extracción (Ext) → salida (StrOutput) con promedios por nivel y `conclusion_exactitud` por API. Añadir `referencia_exactitud`.

- Ejemplo de salida del supervisor (caso "Cumple"):
{
  "activos_exactitud": [
    {
      "nombre": "[api_1_nombre]",
      "exactitud_metodo": [
        { "nivel": "Level I", "recuperacion": 99.75, "promedio": 99.75 },
        { "nivel": "Level II", "recuperacion": 100.10, "promedio": 100.10 },
        { "nivel": "Level III", "recuperacion": 98.70, "promedio": 98.70 }
      ],
      "conclusion_exactitud": "Cumple",
      "criterio_exactitud": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[rango_por_nivel_ej: 98.0–102.0%]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ]
    }
  ],
  "referencia_exactitud": "[lims_run_o_ref_analitica]"
}

- Ejemplo de salida del supervisor (caso "No Cumple"):
{
  "activos_exactitud": [
    {
      "nombre": "[api_2_nombre]",
      "exactitud_metodo": [
        { "nivel": "Level I", "recuperacion": 97.80, "promedio": 97.80 },
        { "nivel": "Level II", "recuperacion": 100.40, "promedio": 100.40 },
        { "nivel": "Level III", "recuperacion": 103.10, "promedio": 103.10 }
      ],
      "conclusion_exactitud": "No Cumple",
      "criterio_exactitud": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[rango_por_nivel_ej: 98.0–102.0%]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ]
    }
  ],
  "referencia_exactitud": "[lims_run_o_ref_analitica]"
}
</REGLAS_DE_SALIDA_ESTRUCTURADA>
"""


RULES_SET_5 = """
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al `structured_extraction_agent`.

- Objetivo: Extraer la información de **precisión del sistema** por API desde reportes LIMS (datos crudos y RSD%) y protocolos (criterios), y estructurarla según `Set5ExtractionModel` (lista de `ActivoPrecisionsistemaStrExt`).

- Plan iterativo (varios ciclos sobre el vectorstore):
  1) Descubrimiento de APIs con precisión del sistema: buscar tablas con columnas "N°" (réplica), "Values" y "Unit".
  2) Extracción por API (un subciclo por API):
     • Datos crudos → `precision_sistema` = [{replica, area_activo}] **solo** si Unit=Area.  
     • RSD% → `rsd_precision_sistema` (si el LIMS lo reporta como "RSD%").  
     • Criterios → `criterio_precision_sistema` desde el Protocolo (tabla de criterios).  
     • Conclusión preliminar → `conclusion_precision_sistema` = "[pendiente_validar]".  
     • Referencia → `referencia_precision_sistema` (ID/código de corrida) para el supervisor.
  3) Trazabilidad obligatoria (ledger interno): source_document (LIMS/Protocolo), page_or_span, query_used, confidence, cleaning_notes.
  4) Normalización mínima:
     • `replica`: mantener como texto del reporte (1..10).  
     • `area_activo`: convertir a float (0–200), unificar coma→punto; omitir si no hay unidad de Area.  
     • No alterar formato de RSD% numérico (0–200).
  5) Relleno de huecos: si tras los ciclos falta evidencia, marcar campos como "[pendiente_validar]" y registrar causa.

- Ejemplo de extracción (Set5ExtractionModel con placeholders):
{
  "activos_precision_sistema": [
    {
      "nombre": "[api_1_nombre]",
      "precision_sistema": [
        { "replica": "1", "area_activo": 99.8 },
        { "replica": "2", "area_activo": 100.2 },
        { "replica": "3", "area_activo": 100.1 },
        { "replica": "4", "area_activo": 99.7 },
        { "replica": "5", "area_activo": 100.0 },
        { "replica": "6", "area_activo": 99.9 }
      ],
      "conclusion_precision_sistema": "[pendiente_validar]",
      "rsd_precision_sistema": 0.85,
      "criterio_precision_sistema": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[umbral_rsd_ej: ≤ 2.0%]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
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
Estas reglas aplican al `reasoning_agent`.

- Regla principal (innegociable): **el razonamiento documentado SIEMPRE precede** a cualquier verificación, clasificación o salida.
- Pasos mínimos por API:
  1) Verificar datos crudos: contar réplicas válidas (Unit=Area) y registrar valores usados.  
  2) Calcular RSD% si no viene del LIMS: RSD% = 100 * (desv_est / promedio). Documentar promedio y desv_est (pasos intermedios).  
  3) Comparar `rsd_precision_sistema` vs `criterio_precision_sistema` (p. ej., ≤ 2.0%).  
  4) Determinar `conclusion_precision_sistema`: si RSD% ≤ umbral → "Cumple", si no → "No Cumple".  
  5) Justificación explícita: anotar umbral, RSD% obtenido y observaciones (p. ej., réplicas omitidas por unidad incorrecta).

- Mini-ejemplo de razonamiento (orden correcto):
  • Réplicas válidas = 6 (todas con Unit=Area). Promedio=99.95; DesvEst=0.85; RSD%=0.85.  
  • Criterio: RSD% ≤ 2.0% → 0.85% ≤ 2.0% ⇒ **Cumple**.  
  • Conclusión global API [api_1_nombre]: "Cumple". Preparar salida para supervisor.
</REGLAS_DE_RAZONAMIENTO>

<REGLAS_DE_SALIDA_ESTRUCTURADA>
Estas reglas aplican al `supervisor`.

- Modelo de salida: `Set5StructuredOutputSupervisor` en **JSON bien formado**. **Solo** el JSON final (sin texto extra).
- Condición: emitir salida **solo después** del razonamiento documentado.
- Integración: copiar listas de réplicas válidas; usar `rsd_precision_sistema` final; fijar `conclusion_precision_sistema`; agregar `referencia_precision_sistema`.

- Ejemplo de salida del supervisor (caso "Cumple"):
{
  "activos_precision_sistema": [
    {
      "nombre": "[api_1_nombre]",
      "precision_sistema": [
        { "replica": "1", "area_activo": 99.8 },
        { "replica": "2", "area_activo": 100.2 },
        { "replica": "3", "area_activo": 100.1 },
        { "replica": "4", "area_activo": 99.7 },
        { "replica": "5", "area_activo": 100.0 },
        { "replica": "6", "area_activo": 99.9 }
      ],
      "conclusion_precision_sistema": "Cumple",
      "criterio_precision_sistema": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[umbral_rsd_ej: ≤ 2.0%]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ],
      "rsd_precision_sistema": 0.85
    }
  ],
  "referencia_precision_sistema": "[lims_run_o_ref_analitica]"
}

- Ejemplo de salida del supervisor (caso "No Cumple"):
{
  "activos_precision_sistema": [
    {
      "nombre": "[api_2_nombre]",
      "precision_sistema": [
        { "replica": "1", "area_activo": 101.5 },
        { "replica": "2", "area_activo": 98.4 },
        { "replica": "3", "area_activo": 102.0 },
        { "replica": "4", "area_activo": 96.8 },
        { "replica": "5", "area_activo": 103.2 },
        { "replica": "6", "area_activo": 95.7 }
      ],
      "conclusion_precision_sistema": "No Cumple",
      "criterio_precision_sistema": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[umbral_rsd_ej: ≤ 2.0%]",
          "criterio_precision_metodo": "[na]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ],
      "rsd_precision_sistema": 3.10
    }
  ],
  "referencia_precision_sistema": "[lims_run_o_ref_analitica]"
}
</REGLAS_DE_SALIDA_ESTRUCTURADA>
"""

RULES_SET_6 = """
<REGLAS_DE_EXTRACCION_ESTRUCTURADA>
Estas reglas aplican al structured_extraction_agent.

- Objetivo: Extraer información de **precisión del método** por API desde reportes LIMS (porcentajes por réplica y RSD%) y protocolo (criterios) y estructurarla según `Set6ExtractionModel` (lista de `ActivoPrecisionMetodoStrExt`).

- Plan iterativo (varios ciclos sobre el vectorstore):
  1) Descubrimiento: localizar tablas con columnas "N°" (réplica) y "Results" (porcentaje), asociadas a la prueba de precisión del método.
  2) Extracción por API (subciclo por API):
     • `precision_metodo` ← lista de {replica, porcentaje_activo} desde LIMS.  
     • `rsd_precision_metodo` ← tomar del LIMS si aparece como "RSD%"; si falta, dejar "[pendiente_validar]" (se calculará en razonamiento).  
     • `criterio_precision_metodo` ← extraer del Protocolo (tabla de criterios; registrar el umbral de RSD%).  
     • `conclusion_precision_metodo` ← inicializar en "[pendiente_validar]".
  3) Trazabilidad obligatoria (ledger interno, no en la salida): source_document (LIMS/Protocolo), page_or_span, query_used, confidence, cleaning_notes.
  4) Normalización mínima:
     • Convertir coma→punto; `porcentaje_activo` en rango 0–200.  
     • Conservar literal de `replica` tal como en el documento.
  5) Deduplificación: si hay múltiples corridas, unificar por (api, replica, run_id), conservando la más completa/reciente; anotar motivo.
  6) Relleno de huecos: si tras los ciclos persisten faltantes, marcar "[pendiente_validar]" y documentar causa en trazabilidad.

- Ejemplo de extracción estructurada (Set6ExtractionModel con placeholders):
{
  "activos_precision_metodo": [
    {
      "nombre": "[api_1_nombre]",
      "precision_metodo": [
        { "replica": "1", "porcentaje_activo": 99.8 },
        { "replica": "2", "porcentaje_activo": 100.3 },
        { "replica": "3", "porcentaje_activo": 100.1 },
        { "replica": "4", "porcentaje_activo": 99.7 },
        { "replica": "5", "porcentaje_activo": 100.0 },
        { "replica": "6", "porcentaje_activo": 99.9 }
      ],
      "conclusion_precision_metodo": "[pendiente_validar]",
      "rsd_precision_metodo": "[pendiente_validar]",
      "criterio_precision_metodo": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[umbral_rsd: <= 2.0%]",
          "criterio_precision_intermedia": "[na]",
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

- REGLA PRINCIPAL: El razonamiento documentado **SIEMPRE** precede a cualquier verificación, clasificación o salida final. Registrar cálculos e inferencias.

- Pasos mínimos por API (documentar explícitamente):
  1) Verificar datos crudos: listar las réplicas válidas y sus porcentajes usados; excluir filas inválidas con motivo.
  2) Cálculos intermedios:
     • promedio = mean(porcentajes)  
     • desv_est = std(porcentajes, n-1)  
     • rsd_calculado = 100 * (desv_est / promedio)  
     (Usar rsd_calculado si `rsd_precision_metodo` no viene del LIMS). Registrar N, promedio, desv_est, RSD%.
  3) Comparación con criterio: contrastar RSD% contra `criterio_precision_metodo` (p. ej., ≤ 2.0%). Si el protocolo exige N mínimo (p. ej., 6), verificar y documentar.
  4) Conclusión global:
     • `conclusion_precision_metodo` = "Cumple" si RSD% ≤ umbral (y N cumple si aplica); de lo contrario "No Cumple".  
     • Justificación breve con números y umbrales aplicados.

- Mini-ejemplo de razonamiento (orden correcto):
  • Réplicas válidas = 6; valores = [99.8, 100.3, 100.1, 99.7, 100.0, 99.9]  
  • promedio = 99.97 ; desv_est = 0.22 ; RSD% = 0.22%  
  • Criterio: RSD% ≤ 2.0% y N≥6 → Cumple  
  • Conclusión API [api_1_nombre] = "Cumple".
</REGLAS_DE_RAZONAMIENTO>

<REGLAS_DE_SALIDA_ESTRUCTURADA>
Estas reglas aplican al supervisor.

- Modelo de salida: `Set6StructuredOutputSupervisor` en **JSON bien formado**. **Solo** el JSON final (sin texto extra).
- Condición: emitir salida únicamente después de que el razonamiento esté documentado.
- Integración: copiar `precision_metodo` depurada; fijar `rsd_precision_metodo` final (del LIMS o calculado); establecer `conclusion_precision_metodo`; incluir `criterio_precision_metodo` y `referencia_precision_metodo`.

- Ejemplo A (caso "Cumple") — Orden: 1) razonamiento → 2) salida
Razonamiento (resumen): N=6; promedio=99.97; desv_est=0.22; RSD%=0.22; umbral ≤2.0% ⇒ Cumple.

Salida final (JSON):
{
  "activos_precision_metodo": [
    {
      "nombre": "[api_1_nombre]",
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
      "criterio_precision_metodo": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[umbral_rsd: <= 2.0%]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ]
    }
  ],
  "referencia_precision_metodo": "[lims_run_o_ref_analitica]"
}

- Ejemplo B (caso "No Cumple") — Orden: 1) razonamiento → 2) salida
Razonamiento (resumen): N=6; promedio=100.2; desv_est=3.1; RSD%=3.09; umbral ≤2.0% ⇒ No Cumple.

Salida final (JSON):
{
  "activos_precision_metodo": [
    {
      "nombre": "[api_2_nombre]",
      "precision_metodo": [
        { "replica": "1", "porcentaje_activo": 104.0 },
        { "replica": "2", "porcentaje_activo": 96.5 },
        { "replica": "3", "porcentaje_activo": 102.0 },
        { "replica": "4", "porcentaje_activo": 97.8 },
        { "replica": "5", "porcentaje_activo": 101.6 },
        { "replica": "6", "porcentaje_activo": 99.1 }
      ],
      "conclusion_precision_metodo": "No Cumple",
      "rsd_precision_metodo": 3.09,
      "criterio_precision_metodo": [
        {
          "criterio_selectividad": "[na]",
          "criterio_linealidad": "[na]",
          "criterio_exactitud": "[na]",
          "criterio_precision_sistema": "[na]",
          "criterio_precision_metodo": "[umbral_rsd: <= 2.0%]",
          "criterio_precision_intermedia": "[na]",
          "criterio_rango": "[na]",
          "criterio_estabilidad_soluciones": "[na]",
          "criterio_estabilidad_fase_movil": "[na]",
          "criterio_robustez": "[na]"
        }
      ]
    }
  ],
  "referencia_precision_metodo": "[lims_run_o_ref_analitica]"
}

— RESTRICCIÓN CRÍTICA (repetida): **RAZONAMIENTO → LUEGO SALIDA**. Cualquier cálculo o inferencia debe documentarse antes de la salida final.
</REGLAS_DE_SALIDA_ESTRUCTURADA>
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
