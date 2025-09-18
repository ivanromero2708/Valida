#!/usr/bin/env python3
"""
Script para probar las rutas correctas de los documentos de PRECISION_SISTEMA
y validar que el RAG pipeline funciona correctamente.
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar los módulos
sys.path.append(str(Path(__file__).parent / "src"))

from src.tools.rag_pipeline_tool import RAGPipelineTool

def test_rutas_precision_sistema():
    """Prueba las rutas correctas de los documentos de PRECISION_SISTEMA"""
    
    # Rutas correctas encontradas
    rutas_correctas = [
        r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\12. Informes de validación\documentos_ejemplos\VALORACION\PRECISION_SISTEMA\REPORTE_PRECISION_SISTEMA\REPORTE_LIMS_PRECISION_SISTEMA.pdf",
        r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\12. Informes de validación\documentos_ejemplos\VALORACION\PRECISION_SISTEMA\DATA_CROMATOGRAFICA\DATA_CROMATOIGRAFICA_PRECISION_SISTEMA.pdf"
    ]
    
    print("=== VERIFICACIÓN DE RUTAS ===")
    for i, ruta in enumerate(rutas_correctas, 1):
        print(f"\n{i}. Verificando: {ruta}")
        if os.path.exists(ruta):
            print(f"   ✅ EXISTE")
            size = os.path.getsize(ruta)
            print(f"   📏 Tamaño: {size:,} bytes")
        else:
            print(f"   ❌ NO EXISTE")
    
    print("\n=== PRUEBA DEL RAG PIPELINE TOOL ===")
    
    # Crear instancia del tool
    rag_tool = RAGPipelineTool()
    
    # Probar cada archivo
    for i, ruta_completa in enumerate(rutas_correctas, 1):
        if not os.path.exists(ruta_completa):
            print(f"\n{i}. ⏭️  Saltando {Path(ruta_completa).name} (no existe)")
            continue
            
        print(f"\n{i}. 🔄 Procesando: {Path(ruta_completa).name}")
        
        # Extraer directorio padre y nombre del archivo
        path_obj = Path(ruta_completa)
        directorio_padre = str(path_obj.parent)
        nombre_archivo = path_obj.name
        
        print(f"   📁 Directorio: {directorio_padre}")
        print(f"   📄 Archivo: {nombre_archivo}")
        
        try:
            # Llamar al RAG pipeline tool
            resultado = rag_tool._run(
                directory=directorio_padre,
                specific_files=[nombre_archivo],
                chunk_size=2000,
                chunk_overlap=250,
                recursive=False
            )
            
            print(f"   ✅ ÉXITO")
            print(f"   📊 Resultado: {resultado[:200]}...")
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

def generar_rutas_correctas_para_mensaje():
    """Genera las rutas correctas en el formato que debe ir en el mensaje"""
    
    rutas_correctas = [
        r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\12. Informes de validación\documentos_ejemplos\VALORACION\PRECISION_SISTEMA\REPORTE_PRECISION_SISTEMA\REPORTE_LIMS_PRECISION_SISTEMA.pdf",
        r"C:\Users\Ivan\OneDrive - Grupo Procaps\Portafolio NTF\16 - I&D 4.0\12. Informes de validación\documentos_ejemplos\VALORACION\PRECISION_SISTEMA\DATA_CROMATOGRAFICA\DATA_CROMATOIGRAFICA_PRECISION_SISTEMA.pdf"
    ]
    
    print("\n=== RUTAS CORRECTAS PARA EL MENSAJE ===")
    print("<LISTA_DOCS>")
    for ruta in rutas_correctas:
        print(f"'{ruta}',")
    print("</LISTA_DOCS>")
    
    # También en formato de lista Python para copiar/pegar
    print("\n=== FORMATO PYTHON ===")
    print("doc_path_list = [")
    for ruta in rutas_correctas:
        print(f'    r"{ruta}",')
    print("]")

if __name__ == "__main__":
    print("🧪 DIAGNÓSTICO DE RUTAS DE PRECISION_SISTEMA")
    print("=" * 60)
    
    test_rutas_precision_sistema()
    generar_rutas_correctas_para_mensaje()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico completado")
