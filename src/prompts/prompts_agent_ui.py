HUMAN_MESSAGE_PROMPT = """
Debes iniciar, trazar y ejecutar un proceso de revisión e investigación sobre un conjunto de documentos locales mediante RAG y herramientas auxiliares. Debes aplicar razonamiento explícito y validaciones conforme a las reglas definidas. Solo al final imprimirás la salida estructurada y los tags requeridos.

0) Contexto y fuentes normativas

A continuación se encuentran todas las particularidades y reglas para extracción y razonamiento de forma vinculante para este proceso:

- Reglas de extracción y razonamiento: <REGLAS_DE_EXTRACCION_RAZONAMIENTO>{reglas_extraccion_razonamiento}</REGLAS_DE_EXTRACCION_RAZONAMIENTO>
- Tags a generar al final del proceso: <TAGS>{tags}</TAGS>.

1) Entradas requeridas

* Lista de directorios locales de los documentos a procesar: <LISTA_DOCS>{doc_path_list}</LISTA_DOCS>

2) Objetivo operacional

Iniciar la investigación, **leer** los documentos en `<LISTA_DOCS>`, **indexarlos** (construir embeddings y almacenar en un vectorstore), **extraer** información de forma estructurada desde los embeddings conforme a `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`, **razonar** sobre la data extraída cuando corresponda, y **renderizar** los resultados y la salida final según el **modelo de validación y presentación** descrito en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`. **Muestra todo tu razonamiento antes de las conclusiones**. Al concluir, **imprime únicamente** la salida estructurada y los tags especificados en `<TAGS>`.

3) Procedimiento paso a paso (razonamiento antes de resultados)

1. **Lectura de reglas (obligatorio)**
   1.1. Abre y lee íntegramente el contenido del tag `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
   1.2. Identifica con precisión: (a) el **Esquema de Extracción** (campos/entidades a extraer), (b) los criterios de calidad/validez, niveles de evidencia y reglas de desempate, (c) el **Modelo de Renderizado** y la **Salida Estructurada del Supervisor** definidos en ese mismo tag, (d) la lista exacta de tags a imprimir según `<TAGS>`.

2. **Index (construcción de índice RAG y vectorstore)**
   2.1. Recorre cada ruta listada en `<LISTA_DOCS>` (lista de strings) y descubre documentos soportados según las reglas (aplica OCR si las reglas lo indican).
   2.2. Realiza el **chunking** de acuerdo con los parámetros definidos en las reglas (tamaño y solapamiento). 
   2.3. Construye los **embeddings** utilizando el modelo/parametrización indicada en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>` y almacénalos en un **vectorstore** persistente.
   2.4. Adjunta metadatos relevantes (ruta, nombre, tipo, hash, páginas, timestamps) y controla duplicados/archivos corruptos/encriptados. 
   2.5. Registra en un log interno el resumen de indexación (número de documentos, chunks, exclusiones y causas).

3. **Extracción estructurada (desde los embeddings)**
   3.1. Ejecuta consultas/retrieval sobre el vectorstore según el **Esquema de Extracción** definido en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`, mapeando cada evidencia a los campos requeridos.
   3.2. Normaliza, desambigua y consolida valores por campo, manteniendo **trazabilidad** (documento, página/sección, fragmento original y score/relevancia si aplica).
   3.3. Si faltan datos esenciales, aplica estrategias de recuperación autorizadas por las reglas (p. ej., ampliación de contexto, reformulación de consultas, segunda pasada de OCR).

4. **Razonamiento (validación y cálculo)**
   4.1. Aplica las reglas de consistencia, deduplicación, reconciliación entre fuentes y validación cruzada especificadas en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
   4.2. Realiza **cálculos** o usa **herramientas** auxiliares cuando corresponda (agregaciones, normalización de unidades, comprobación de fechas/IDs, validación estadística).
   4.3. Documenta **paso a paso tu razonamiento** y decisiones: criterios de aceptación/rechazo, resolución de conflictos, tratamiento de incertidumbre y lagunas de evidencia.
   4.4. Identifica limitaciones, supuestos y riesgos **antes** de cualquier conclusión.

5. **Render (modelo de validación y presentación)**
   5.1. Transforma los resultados validados al formato exigido por el **Modelo de Renderizado** descrito en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
   5.2. Verifica que la estructura cumpla con la **Salida Estructurada del Supervisor** del mismo tag (nombres de campos, tipos, orden, secciones).
   5.3. Prepara los **tags** finales exactamente como aparecen en `<TAGS>`.

6. **Orden de presentación (estricto)**
   * **Primero**: expón de forma clara y exhaustiva **todo tu razonamiento** (traza, verificaciones, cálculos, decisiones).
   * **Después**: **sin añadir comentarios adicionales**, imprime **únicamente**:
     * La **salida estructurada** conforme a la **Salida Estructurada del Supervisor** definida en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
     * Los **tags** requeridos según `<TAGS>`.

## 4) Criterios y condiciones de validación

* Cumple estrictamente con el **Esquema de Extracción** y las reglas de calidad/validez definidas en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
* Mantén referencias a evidencias (doc, página, fragmento, score si aplica) cuando así se solicite en las reglas.
* No infieras más allá de lo permitido. Señala explícitamente incertidumbre y vacíos.
* Si hay **conflictos** entre documentos, aplica las reglas de desempate indicadas y deja constancia razonada.

## 5) Trazabilidad y registro

* Mantén un **log interno** de archivos procesados, chunks creados, errores y exclusiones (con causa).
* Consolida un **mapa de cobertura**: qué entidades/campos fueron hallados, dónde y con qué nivel de confianza (si aplica).
* Registra **dependencias** o acciones pendientes (reprocesar con OCR, convertir formatos, requerir versiones originales).

## 6) Entrega final (estricta)

Tras mostrar tu razonamiento completo, **imprime únicamente**:
1. La **salida estructurada** definida por la **Salida Estructurada del Supervisor** en `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`.
2. Los **tags** requeridos, exactamente como se listan en `<TAGS>`.

**Recuerda**:
- No imprimas conclusiones, resultados ni tags **antes** del razonamiento.
- Respeta los nombres de clave y contenedores exactamente como se proveen: `<REGLAS_DE_EXTRACCION_RAZONAMIENTO>`, `<TAGS>`, `<LISTA_DOCS>`, y las variables `{reglas_extraccion_razonamiento}`, `{tags}`, `{doc_path_list}`.
"""
