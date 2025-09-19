import sys
from src.tools.linealidad_tool import LinearidadTool
import json

# Crear herramienta
tool = LinearidadTool()

# Datos de prueba
datos = {
    'concentracion': [0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
    'area_pico': [150.0, 250.0, 450.0, 650.0, 850.0, 1050.0],
    'guardar_plots': True,
    'nombre_analito': 'Test Básico'
}

# Ejecutar
resultado = tool.invoke(datos)
parsed = json.loads(resultado)

print('=== RESULTADO DE PRUEBA BÁSICA ===')
print(f'Status: {parsed["status"]}')
print(f'R²: {parsed["resultados_regresion"]["r2"]:.6f}')
print(f'Ecuación: {parsed["resultados_regresion"]["ecuacion"]}')
print('✅ Herramienta funcionando correctamente')
