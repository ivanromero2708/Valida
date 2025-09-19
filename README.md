# Valida - Sistema de Generación de Informes de Validación

## 📋 Descripción

**Valida** es un sistema automatizado basado en LangGraph para la generación de informes de validación farmacéutica. El sistema consolida múltiples secciones de validación en un único documento DOCX utilizando plantillas predefinidas y modelos de datos estructurados.

## 🏗️ Arquitectura

El proyecto utiliza **LangGraph** con el patrón Command para orquestar la generación de informes de validación. La arquitectura incluye:

- **Nodos LangGraph**: Procesamiento distribuido de diferentes secciones de validación
- **Modelos de Datos**: Estructuras Pydantic para validación de datos de entrada
- **Plantillas DOCX**: Templates consolidados para generación de documentos
- **Renderizado Unificado**: Un solo nodo que maneja todas las secciones de validación

## 📁 Estructura del Proyecto

```plain_text
Valida/
├── src/
│   ├── agents/                 # Agentes LangGraph
│   ├── config/                 # Configuración del sistema
│   ├── databases/              # Conectores de base de datos
│   ├── graph/                  # Definición del grafo LangGraph
│   │   ├── nodes/              # Nodos del grafo
│   │   └── builder.py          # Constructor del grafo principal
│   ├── models/                 # Modelos de datos Pydantic
│   ├── templates/              # Plantillas DOCX
│   ├── tools/                  # Herramientas auxiliares
│   └── utils/                  # Utilidades generales
├── tests/                      # Pruebas y ejemplos
├── tmp_files/                  # Archivos temporales
├── requirements.txt            # Dependencias Python
├── langgraph.json             # Configuración LangGraph
└── README.md                  # Este archivo
```

## 🧪 Secciones de Validación Soportadas

El sistema genera informes para las siguientes secciones de validación:

1. **Linealidad del Sistema** - Análisis multi-activos con regresión lineal
2. **Exactitud del Método** - Porcentajes de recuperación por niveles
3. **Materiales e Insumos** - Inventario de reactivos, equipos y columnas
4. **Precisión del Sistema** - RSD de inyecciones replicadas
5. **Repetibilidad** - Precisión intra-día del método
6. **Precisión Intermedia** - Precisión inter-día/analista
7. **Estabilidad de Soluciones** - Estabilidad temporal de muestras
8. **Estabilidad de Fase Móvil** - Variación de tiempos de retención
9. **Robustez** - Evaluación de factores críticos

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.9+
- Conda (recomendado)

### Instalación

1. **Crear y activar entorno virtual:**

```bash
conda create -n valida python=3.9
conda activate valida
```

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## 💻 Uso

### Desarrollo Local

1. **Iniciar servidor LangGraph:**

```bash
langgraph dev
```

2. **Ejecutar pruebas:**

```bash
python -m pytest tests/
```

3. **Generar informe de ejemplo:**

```bash
python tests/final.py
```

### Uso Programático

```python
from src.graph.builder import build_validation_graph
from src.models.validation_data import ValidationRequest

# Crear grafo de validación
graph = build_validation_graph()

# Preparar datos de validación
validation_data = ValidationRequest(
    project_info={
        "title": "Validación Método HPLC",
        "product": "Producto Farmacéutico X",
        "analyst": "Analista Principal"
    },
    linearity_data=...,
    accuracy_data=...,
    # ... otros datos
)

# Ejecutar generación de informe
result = graph.invoke({
    "validation_request": validation_data,
    "output_path": "informe_validacion.docx"
})
```

## 🔧 Configuración

### LangGraph

El archivo `langgraph.json` define los grafos disponibles:

```json
{
    "dependencies": ["."],
    "graphs": {
        "validation_report": "./src/graph/builder.py:build_validation_graph"
    },
    "env": ".env"
}
```

### Variables de Entorno

Crear archivo `.env` con:

```env
# APIs
OPENAI_API_KEY=tu_api_key_aqui
LANGSMITH_API_KEY=tu_langsmith_key

# Configuración
TEMPLATE_PATH=./src/templates/
OUTPUT_PATH=./output/
LOG_LEVEL=INFO
```

## 📊 Modelos de Datos

El sistema utiliza modelos Pydantic para validación de datos:

```python
from src.models.validation_data import (
    LinearityData,
    AccuracyData,
    MaterialsData,
    PrecisionData,
    # ... otros modelos
)
```

## 🧪 Testing

Ejecutar suite completa de pruebas:

```bash
# Todas las pruebas
python -m pytest

# Con cobertura
python -m pytest --cov=src

# Prueba específica
python -m pytest tests/test_validation_models.py
```

## 📝 Contribución

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es propiedad de **Grupo Procaps** - Todos los derechos reservados.

## 🆘 Soporte

Para soporte técnico, contactar:

- **Equipo I&D 4.0**: <iromero@procaps.com.co>

- **Documentación**: [Wiki Interno](link-interno)

## 📈 Roadmap

- [ ] Integración con LIMS
- [ ] Soporte para validaciones ICH Q2
- [ ] Dashboard web interactivo
- [ ] Exportación a múltiples formatos
- [ ] Validación automática de criterios regulatorios


# LinearidadTool - Herramienta de Análisis de Linealidad

## Descripción

`LinearidadTool` es una herramienta diseñada específicamente para el flujo de agentes de validación farmacéutica. Realiza análisis de regresión lineal para curvas de calibración, calculando parámetros estadísticos esenciales y generando visualizaciones profesionales.

## Características Principales

### ✅ Diseño para Agentes
- **Sin fallbacks**: Recibe datos directamente del flujo de agentes
- **Entrada estructurada**: Validación estricta con Pydantic
- **Salida JSON**: Formato estructurado para procesamiento posterior
- **Manejo de errores**: Respuestas consistentes en caso de fallo

### 📊 Análisis Estadístico
- Regresión lineal (pendiente, intercepto, R²)
- Análisis de residuales (media, desviación estándar, valores extremos)
- %RSD por nivel de concentración (para replicados)
- Criterios de aceptación farmacéuticos (R² ≥ 0.995)

### 📈 Visualizaciones
- Gráfico de regresión lineal con ecuación y R²
- Gráfico de residuales para evaluación de linealidad
- Estilo profesional (Times New Roman, colores consistentes)
- Exportación a PNG y/o base64

## Uso en el Flujo de Agentes

```python
from tools.linealidad_tool import LinearidadTool

# Instanciar la herramienta
tool = LinearidadTool()

# Datos recibidos del agente anterior
concentraciones = [0.08, 0.16, 0.20, 0.24, 0.28, 0.32]  # mg/mL
areas = [353.2, 581.4, 695.8, 809.1, 923.7, 1037.2]     # Área de pico

# Invocar la herramienta
resultado_json = tool.invoke({
    "concentracion": concentraciones,
    "area_pico": areas,
    "nombre_analito": "Principio Activo XYZ"
})

# El resultado es un JSON string
import json
resultado = json.loads(resultado_json)
print(f"R² = {resultado['resultados_regresion']['r2']:.6f}")
```

## Parámetros de Entrada

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `concentracion` | `List[float]` | ✅ | Lista de concentraciones (mg/mL) |
| `area_pico` | `List[float]` | ✅ | Lista de áreas de pico correspondientes |
| `devolver_base64` | `bool` | ❌ | Incluir gráficos en base64 (default: False) |
| `nombre_analito` | `str` | ❌ | Nombre del analito para títulos |

**Nota**: Los gráficos PNG siempre se generan y guardan en `src/images/`.

## Estructura de Respuesta

```json
{
  "status": "success",
  "timestamp": "2024-01-15T10:30:00",
  "input_data": {
    "n_puntos": 6,
    "concentracion_min": 0.08,
    "concentracion_max": 0.32,
    "nombre_analito": "Principio Activo XYZ"
  },
  "resultados_regresion": {
    "pendiente_m": 2850.125,
    "intercepto_b": 125.45,
    "r2": 0.999654,
    "ecuacion": "y = 2850.125000x + 125.450000"
  },
  "analisis_residuales": {
    "media": 0.023,
    "desv_est": 1.245,
    "max_absoluto": 2.1,
    "min": -1.8,
    "max": 2.1
  },
  "rsd_por_nivel_pct": {
    "0.2": 1.25,
    "0.5": 0.89
  },
  "datos_predichos": {
    "y_predicho": [353.46, 581.47, ...],
    "residuales": [-0.26, -0.07, ...]
  },
  "plots": {
    "regresion_png_path": "C:/path/to/src/images/linealidad_regresion_uuid-1234.png",
    "residuales_png_path": "C:/path/to/src/images/linealidad_residuales_uuid-5678.png",
    "regresion_base64": null,
    "residuales_base64": null
  },
  "criterios_aceptacion": {
    "r2_minimo": 0.995,
    "r2_cumple": true,
    "residuales_max_absoluto": 2.1
  }
}
```

## Validaciones de Entrada

### ✅ Validaciones Automáticas
- Longitudes iguales de `concentracion` y `area_pico`
- Valores positivos en ambas listas
- Mínimo 2 puntos de datos
- Tipos de datos correctos

### ❌ Casos de Error
```python
# Error: Longitudes diferentes
tool.invoke({
    "concentracion": [0.1, 0.2, 0.3],
    "area_pico": [100, 200]  # ❌ Falta un valor
})

# Error: Valores negativos
tool.invoke({
    "concentracion": [-0.1, 0.2],  # ❌ Valor negativo
    "area_pico": [100, 200]
})
```

## Diferencias con la Versión Anterior

### ❌ Eliminado (linealidad_V2.py)
- Lectura de archivos DOCX
- Fallback automático a datos sintéticos
- Decorador `@tool` de LangChain
- Parsing de celdas con unidades
- **Parámetro `carpeta_salida`**: Ubicación fija en `src/images/`
- **Parámetro `guardar_plots`**: Siempre genera gráficos
- **Nombres con timestamp**: Reemplazado por UUIDs únicos

### ✅ Mejorado (linealidad_tool.py)
- Herencia de `BaseTool` para mejor integración
- Validación estricta con Pydantic
- Manejo de errores robusto
- Salida JSON estructurada
- Documentación completa
- Soporte asíncrono
- **Ubicación fija de imágenes**: `src/images/` con nombres UUID
- **Generación automática**: Siempre crea gráficos PNG
- **Sin parámetros de carpeta**: Estructura consistente del proyecto

## Pruebas

### Ejecutar Suite de Pruebas
```bash
cd tests
python test_linealidad_tool.py
```

### Generar Datos Sintéticos
```python
from tests.datos_sinteticos_linealidad import GeneradorDatosSinteticos

generador = GeneradorDatosSinteticos()
datos = generador.generar_caso_farmaceutico_realista()
```

## Integración con LangGraph

```python
from langgraph import StateGraph
from tools.linealidad_tool import LinearidadTool

def nodo_linealidad(state):
    """Nodo de LangGraph para análisis de linealidad."""
    tool = LinearidadTool()
    
    # Extraer datos del estado
    concentraciones = state.get("concentraciones_extraidas")
    areas = state.get("areas_extraidas")
    
    # Ejecutar análisis
    resultado = tool.invoke({
        "concentracion": concentraciones,
        "area_pico": areas,
        "nombre_analito": state.get("nombre_analito", "Desconocido")
    })
    
    # Actualizar estado
    state["analisis_linealidad"] = json.loads(resultado)
    return state

# Añadir al grafo
graph = StateGraph(...)
graph.add_node("linealidad", nodo_linealidad)
```

## Criterios de Aceptación Farmacéuticos

| Parámetro | Criterio | Implementado |
|-----------|----------|--------------|
| R² | ≥ 0.995 | ✅ |
| Residuales | Distribución aleatoria | ✅ (gráfico) |
| %RSD por nivel | ≤ 2.0% | ✅ (calculado) |
| Intercepto | Significativo estadísticamente | ⏳ (futuro) |

## Dependencias

```txt
numpy>=1.21.0
matplotlib>=3.5.0
pydantic>=1.8.0
langchain-core>=0.1.0
```

## Estructura de Archivos

```text
src/
├── tools/
│   └── linealidad_tool.py
└── images/                    # ← Creado automáticamente
    ├── linealidad_regresion_uuid-1234.png
    └── linealidad_residuales_uuid-5678.png
```

## Notas de Desarrollo

- **Thread-safe**: Puede ejecutarse en paralelo
- **Memory-efficient**: Cierra figuras automáticamente
- **Error-resilient**: Manejo robusto de excepciones
- **Extensible**: Fácil añadir nuevos parámetros estadísticos
- **UUID-based naming**: Evita conflictos de nombres de archivos
- **Fixed location**: Imágenes siempre en `src/images/`
