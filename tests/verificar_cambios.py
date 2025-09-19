#!/usr/bin/env python3
"""
Script para verificar los cambios en LinearidadTool
- Ubicación fija de imágenes en src/images/
- Nombres con UUID
- Sin parámetro carpeta_salida
"""

import sys
import json
from pathlib import Path

# Añadir src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    print("=== VERIFICACIÓN DE CAMBIOS EN LINEARIDAD TOOL ===\n")
    
    try:
        from tools.linealidad_tool import LinearidadTool
        
        # Crear herramienta
        tool = LinearidadTool()
        print(f"✅ Herramienta creada: {tool.name}")
        
        # Datos de prueba
        datos = {
            'concentracion': [0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
            'area_pico': [150.0, 250.0, 450.0, 650.0, 850.0, 1050.0],
            'nombre_analito': 'Verificación UUID'  # Siempre guarda en src/images/
        }
        
        print("📊 Ejecutando análisis...")
        resultado_json = tool.invoke(datos)
        resultado = json.loads(resultado_json)
        
        if resultado['status'] == 'success':
            print("✅ Análisis exitoso")
            print(f"   R²: {resultado['resultados_regresion']['r2']:.6f}")
            
            # Verificar rutas de imágenes
            plots = resultado.get('plots', {})
            reg_path = plots.get('regresion_png_path')
            res_path = plots.get('residuales_png_path')
            
            print("\n📁 VERIFICACIÓN DE RUTAS:")
            
            if reg_path:
                reg_file = Path(reg_path)
                print(f"   Regresión: {reg_path}")
                print(f"   - Existe: {'✅' if reg_file.exists() else '❌'}")
                print(f"   - En src/images/: {'✅' if 'src/images' in str(reg_file) else '❌'}")
                print(f"   - Nombre UUID: {'✅' if len(reg_file.stem.split('_')[-1]) == 36 else '❌'}")
            
            if res_path:
                res_file = Path(res_path)
                print(f"   Residuales: {res_path}")
                print(f"   - Existe: {'✅' if res_file.exists() else '❌'}")
                print(f"   - En src/images/: {'✅' if 'src/images' in str(res_file) else '❌'}")
                print(f"   - Nombre UUID: {'✅' if len(res_file.stem.split('_')[-1]) == 36 else '❌'}")
            
            # Verificar directorio src/images
            images_dir = src_dir / "images"
            print(f"\n📂 Directorio src/images/:")
            print(f"   - Creado: {'✅' if images_dir.exists() else '❌'}")
            if images_dir.exists():
                png_files = list(images_dir.glob("*.png"))
                print(f"   - Archivos PNG: {len(png_files)}")
                for png_file in png_files:
                    print(f"     • {png_file.name}")
            
            print(f"\n🎉 VERIFICACIÓN COMPLETADA")
            
        else:
            print(f"❌ Error en análisis: {resultado.get('error_message', 'Desconocido')}")
            
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
