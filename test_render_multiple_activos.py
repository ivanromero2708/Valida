#!/usr/bin/env python3
"""
Script de prueba para verificar el procesamiento de múltiples activos
con gráficas individuales en render_validation_report.py
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.graph.nodes.render_validation_report import RenderValidationReport

def test_process_activos_images():
    """Prueba la función _process_activos_images con datos de ejemplo."""
    
    # Crear instancia del renderizador
    renderer = RenderValidationReport()
    
    # Datos de ejemplo que simula la salida del supervisor con múltiples activos
    test_context = {
        "activos_linealidad": [
            {
                "nombre": "Paracetamol",
                "linealidad_sistema": [
                    {"nivel": "I (50%)", "replica": 1, "concentracion": 0.06, "area_pico": 150100},
                    {"nivel": "I (50%)", "replica": 2, "concentracion": 0.06, "area_pico": 149900}
                ],
                "rsd_factor": 1.5,
                "pendiente": 2500000,
                "intercepto": 1000,
                "r": 0.9999,
                "r2": 0.9998,
                "porcentaje_intercepto": 1.2,
                "cumple_global": "Cumple",
                "criterio_linealidad": "Coeficiente de correlación (r) ≥ 0.995",
                "regresion_png_path": "C:/Users/Ivan/OneDrive - Grupo Procaps/Portafolio NTF/16 - I&D 4.0/12. Informes de validación/Valida/src/images/linealidad_regresion_paracetamol_12345.png",
                "residuales_png_path": "C:/Users/Ivan/OneDrive - Grupo Procaps/Portafolio NTF/16 - I&D 4.0/12. Informes de validación/Valida/src/images/linealidad_residuales_paracetamol_12345.png"
            },
            {
                "nombre": "Ibuprofeno",
                "linealidad_sistema": [
                    {"nivel": "I (50%)", "replica": 1, "concentracion": 0.08, "area_pico": 180100},
                    {"nivel": "I (50%)", "replica": 2, "concentracion": 0.08, "area_pico": 179900}
                ],
                "rsd_factor": 1.2,
                "pendiente": 2200000,
                "intercepto": 800,
                "r": 0.9998,
                "r2": 0.9996,
                "porcentaje_intercepto": 0.8,
                "cumple_global": "Cumple",
                "criterio_linealidad": "Coeficiente de correlación (r) ≥ 0.995",
                "regresion_png_path": "C:/Users/Ivan/OneDrive - Grupo Procaps/Portafolio NTF/16 - I&D 4.0/12. Informes de validación/Valida/src/images/linealidad_regresion_ibuprofeno_67890.png",
                "residuales_png_path": "C:/Users/Ivan/OneDrive - Grupo Procaps/Portafolio NTF/16 - I&D 4.0/12. Informes de validación/Valida/src/images/linealidad_residuales_ibuprofeno_67890.png"
            }
        ],
        "referencia_linealidad": "HT001XXXXXX"
    }
    
    print("=== PRUEBA DE PROCESAMIENTO DE MÚLTIPLES ACTIVOS ===")
    print(f"Número de activos a procesar: {len(test_context['activos_linealidad'])}")
    
    # Simular DocxTemplate (None para esta prueba)
    mock_doc = None
    
    try:
        # Procesar el contexto
        processed_context = renderer._process_activos_images(mock_doc, test_context)
        
        print("\n=== RESULTADOS ===")
        print(f"Activos procesados: {len(processed_context.get('activos_linealidad', []))}")
        
        for i, activo in enumerate(processed_context.get('activos_linealidad', [])):
            nombre = activo.get('nombre', f'Activo_{i+1}')
            regresion = activo.get('regresion_png_path', 'No definido')
            residuales = activo.get('residuales_png_path', 'No definido')
            
            print(f"\nActivo {i+1}: {nombre}")
            print(f"  - Regresión: {type(regresion).__name__}")
            print(f"  - Residuales: {type(residuales).__name__}")
            
            if isinstance(regresion, str):
                print(f"    Ruta regresión: {regresion}")
            if isinstance(residuales, str):
                print(f"    Ruta residuales: {residuales}")
        
        print("\n✅ Prueba completada exitosamente")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando pruebas del renderizador con múltiples activos...")
    success = test_process_activos_images()
    
    if success:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
    else:
        print("\n💥 Algunas pruebas fallaron.")
        sys.exit(1)
