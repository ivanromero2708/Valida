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
