#!/usr/bin/env python3
"""
Prueba rápida de LinearidadTool
"""

import sys
from pathlib import Path

# Añadir src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from tools.linealidad_tool import LinearidadTool
    import json
    
    print("=== PRUEBA RÁPIDA DE LINEARIDAD TOOL ===\n")
    
    # Crear herramienta
    tool = LinearidadTool()
    print(f"✅ Herramienta creada: {tool.name}")
    print(f"📝 Descripción: {tool.description}\n")
    
    # Datos de prueba (linealidad perfecta)
    datos_prueba = {
        'concentracion': [0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
        'area_pico': [150.0, 250.0, 450.0, 650.0, 850.0, 1050.0],
        'guardar_plots': False,  # No guardar para prueba rápida
        'nombre_analito': 'Prueba Rápida'
    }
    
    print("📊 Datos de entrada:")
    print(f"   Concentraciones: {datos_prueba['concentracion']}")
    print(f"   Áreas: {datos_prueba['area_pico']}\n")
    
    # Ejecutar herramienta usando invoke()
    print("🚀 Ejecutando tool.invoke()...")
    resultado_json = tool.invoke(datos_prueba)
    
    # Parsear resultado
    resultado = json.loads(resultado_json)
    
    print("✅ Ejecución exitosa!\n")
    print("📈 RESULTADOS:")
    print(f"   Status: {resultado['status']}")
    print(f"   R²: {resultado['resultados_regresion']['r2']:.6f}")
    print(f"   Ecuación: {resultado['resultados_regresion']['ecuacion']}")
    print(f"   Pendiente: {resultado['resultados_regresion']['pendiente_m']:.3f}")
    print(f"   Intercepto: {resultado['resultados_regresion']['intercepto_b']:.3f}")
    
    # Verificar criterios
    r2_cumple = resultado['criterios_aceptacion']['r2_cumple']
    print(f"\n🎯 Criterios de aceptación:")
    print(f"   R² ≥ 0.995: {'✅ SÍ' if r2_cumple else '❌ NO'}")
    
    print(f"\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Verifica que los archivos estén en las rutas correctas")
except Exception as e:
    print(f"💥 Error inesperado: {e}")
    import traceback
    traceback.print_exc()
