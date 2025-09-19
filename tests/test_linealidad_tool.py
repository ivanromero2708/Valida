"""
Script de prueba para LinearidadTool
-----------------------------------
Prueba exhaustiva de la herramienta de linealidad usando tool.invoke()
con diferentes conjuntos de datos sintéticos y casos de error.

Uso:
    python test_linealidad_tool.py

Requisitos:
    - LinearidadTool debe estar en el path
    - Datos sintéticos disponibles
    - Librerías: numpy, matplotlib, pydantic, langchain_core
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import traceback

# Añadir el directorio src al path para importar las herramientas
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from tools.linealidad_tool import LinearidadTool
    from datos_sinteticos_linealidad import (
        GeneradorDatosSinteticos,
        obtener_conjunto_datos,
        generar_casos_error,
        CONJUNTOS_DATOS_PRUEBA
    )
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que los archivos estén en las rutas correctas")
    sys.exit(1)


class TestLinealidadTool:
    """Clase para ejecutar pruebas de la herramienta de linealidad."""
    
    def __init__(self):
        """Inicializa el tester con la herramienta y generador de datos."""
        self.tool = LinearidadTool()
        self.generador = GeneradorDatosSinteticos(seed=42)
        self.resultados_pruebas = []
        
        # Crear directorio de salida para pruebas
        self.output_dir = current_dir / "outputs_test_linealidad"
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"=== INICIANDO PRUEBAS DE LINEALIDAD TOOL ===")
        print(f"Directorio de salida: {self.output_dir}")
        print(f"Herramienta: {self.tool.name}")
        print(f"Descripción: {self.tool.description}\n")
    
    def ejecutar_prueba(
        self, 
        nombre: str, 
        datos: Dict[str, Any], 
        esperado_exitoso: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Ejecuta una prueba individual de la herramienta.
        
        Args:
            nombre: Nombre descriptivo de la prueba
            datos: Dict con concentracion y area_pico
            esperado_exitoso: Si se espera que la prueba sea exitosa
            **kwargs: Parámetros adicionales para la herramienta
            
        Returns:
            Dict con resultados de la prueba
        """
        print(f"🧪 Ejecutando prueba: {nombre}")
        print(f"   Descripción: {datos.get('descripcion', 'N/A')}")
        
        # Parámetros por defecto
        params = {
            "concentracion": datos["concentracion"],
            "area_pico": datos["area_pico"],
            "devolver_base64": False,
            "nombre_analito": datos.get("analito", f"Test_{nombre}")
        }
        
        # Sobrescribir con parámetros adicionales
        params.update(kwargs)
        
        resultado_prueba = {
            "nombre": nombre,
            "parametros": params.copy(),
            "exitoso": False,
            "resultado": None,
            "error": None,
            "tiempo_ejecucion": None
        }
        
        try:
            import time
            inicio = time.time()
            
            # ¡AQUÍ ESTÁ EL INVOKE QUE SOLICITASTE!
            resultado_json = self.tool.invoke(params)
            
            fin = time.time()
            resultado_prueba["tiempo_ejecucion"] = round(fin - inicio, 3)
            
            # Parsear resultado JSON
            resultado_dict = json.loads(resultado_json)
            resultado_prueba["resultado"] = resultado_dict
            resultado_prueba["exitoso"] = (resultado_dict.get("status") == "success")
            
            if resultado_prueba["exitoso"]:
                r2 = resultado_dict["resultados_regresion"]["r2"]
                print(f"   ✅ ÉXITO - R² = {r2:.6f} (tiempo: {resultado_prueba['tiempo_ejecucion']}s)")
                
                # Verificar archivos generados
                plots = resultado_dict.get("plots", {})
                if plots.get("regresion_png_path"):
                    if os.path.exists(plots["regresion_png_path"]):
                        print(f"   📊 Gráfico regresión: {plots['regresion_png_path']}")
                    else:
                        print(f"   ⚠️  Gráfico regresión no encontrado: {plots['regresion_png_path']}")
                
                if plots.get("residuales_png_path"):
                    if os.path.exists(plots["residuales_png_path"]):
                        print(f"   📊 Gráfico residuales: {plots['residuales_png_path']}")
                    else:
                        print(f"   ⚠️  Gráfico residuales no encontrado: {plots['residuales_png_path']}")
                        
            else:
                error_msg = resultado_dict.get("error_message", "Error desconocido")
                print(f"   ❌ FALLO - {error_msg}")
                resultado_prueba["error"] = error_msg
                
        except Exception as e:
            resultado_prueba["error"] = str(e)
            print(f"   💥 EXCEPCIÓN - {str(e)}")
            if not esperado_exitoso:
                print(f"   ℹ️  Error esperado para esta prueba")
            else:
                print(f"   🔍 Traceback:")
                traceback.print_exc()
        
        print()  # Línea en blanco
        self.resultados_pruebas.append(resultado_prueba)
        return resultado_prueba
    
    def probar_conjuntos_predefinidos(self):
        """Prueba todos los conjuntos de datos predefinidos."""
        print("📋 PROBANDO CONJUNTOS PREDEFINIDOS\n")
        
        for nombre in CONJUNTOS_DATOS_PRUEBA:
            datos = obtener_conjunto_datos(nombre)
            self.ejecutar_prueba(f"predefinido_{nombre}", datos)
    
    def probar_datos_generados(self):
        """Prueba datos generados dinámicamente."""
        print("🎲 PROBANDO DATOS GENERADOS DINÁMICAMENTE\n")
        
        # Linealidad perfecta
        datos_perfectos = self.generador.generar_linealidad_perfecta()
        self.ejecutar_prueba("generado_perfecto", datos_perfectos)
        
        # Con ruido
        datos_ruido = self.generador.generar_linealidad_con_ruido(ruido_pct=1.5)
        self.ejecutar_prueba("generado_con_ruido", datos_ruido)
        
        # Con replicados
        datos_replicados = self.generador.generar_con_replicados()
        self.ejecutar_prueba("generado_replicados", datos_replicados)
        
        # Rango amplio
        datos_amplio = self.generador.generar_rango_amplio()
        self.ejecutar_prueba("generado_rango_amplio", datos_amplio)
        
        # Caso farmacéutico realista
        datos_farm = self.generador.generar_caso_farmaceutico_realista()
        self.ejecutar_prueba("generado_farmaceutico", datos_farm)
    
    def probar_parametros_opcionales(self):
        """Prueba diferentes configuraciones de parámetros opcionales."""
        print("⚙️  PROBANDO PARÁMETROS OPCIONALES\n")
        
        datos_base = obtener_conjunto_datos("farmaceutico")
        
        # Solo base64 (sin archivos PNG adicionales)
        self.ejecutar_prueba(
            "con_base64", 
            datos_base,
            devolver_base64=True,
            nombre_analito="Test Con Base64"
        )
        
        # Solo archivos PNG (comportamiento por defecto)
        self.ejecutar_prueba(
            "solo_png", 
            datos_base,
            devolver_base64=False,
            nombre_analito="Test Solo PNG"
        )
        
        # Ambos: PNG y base64
        self.ejecutar_prueba(
            "png_y_base64", 
            datos_base,
            devolver_base64=True,
            nombre_analito="Test PNG y Base64"
        )
    
    def probar_casos_error(self):
        """Prueba casos que deben generar errores."""
        print("🚨 PROBANDO CASOS DE ERROR\n")
        
        casos_error = generar_casos_error()
        
        for nombre, caso in casos_error.items():
            print(f"🧪 Probando error: {nombre}")
            print(f"   Error esperado: {caso['error_esperado']}")
            
            try:
                resultado_json = self.tool.invoke({
                    "concentracion": caso["concentracion"],
                    "area_pico": caso["area_pico"]
                })
                
                resultado = json.loads(resultado_json)
                if resultado.get("status") == "error":
                    print(f"   ✅ Error manejado correctamente: {resultado.get('error_message', 'N/A')}")
                else:
                    print(f"   ⚠️  Se esperaba error pero fue exitoso")
                    
            except Exception as e:
                print(f"   ✅ Excepción capturada: {str(e)}")
            
            print()
    
    def generar_reporte_final(self):
        """Genera un reporte final de todas las pruebas."""
        print("📊 REPORTE FINAL DE PRUEBAS\n")
        
        total = len(self.resultados_pruebas)
        exitosos = sum(1 for r in self.resultados_pruebas if r["exitoso"])
        fallidos = total - exitosos
        
        print(f"Total de pruebas: {total}")
        print(f"Exitosas: {exitosos} ({exitosos/total*100:.1f}%)")
        print(f"Fallidas: {fallidos} ({fallidos/total*100:.1f}%)")
        print()
        
        if fallidos > 0:
            print("❌ PRUEBAS FALLIDAS:")
            for r in self.resultados_pruebas:
                if not r["exitoso"]:
                    print(f"   - {r['nombre']}: {r.get('error', 'Error desconocido')}")
            print()
        
        # Estadísticas de R²
        r2_values = []
        for r in self.resultados_pruebas:
            if r["exitoso"] and r["resultado"]:
                r2 = r["resultado"].get("resultados_regresion", {}).get("r2")
                if r2 is not None:
                    r2_values.append(r2)
        
        if r2_values:
            print(f"📈 ESTADÍSTICAS DE R²:")
            print(f"   Promedio: {sum(r2_values)/len(r2_values):.6f}")
            print(f"   Mínimo: {min(r2_values):.6f}")
            print(f"   Máximo: {max(r2_values):.6f}")
            print(f"   R² ≥ 0.995: {sum(1 for r2 in r2_values if r2 >= 0.995)}/{len(r2_values)}")
        
        # Guardar reporte detallado
        reporte_path = self.output_dir / "reporte_pruebas.json"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            json.dump({
                "resumen": {
                    "total": total,
                    "exitosos": exitosos,
                    "fallidos": fallidos,
                    "porcentaje_exito": exitosos/total*100 if total > 0 else 0
                },
                "estadisticas_r2": {
                    "valores": r2_values,
                    "promedio": sum(r2_values)/len(r2_values) if r2_values else None,
                    "minimo": min(r2_values) if r2_values else None,
                    "maximo": max(r2_values) if r2_values else None
                },
                "pruebas_detalladas": self.resultados_pruebas
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado en: {reporte_path}")
    
    def ejecutar_todas_las_pruebas(self):
        """Ejecuta todas las pruebas disponibles."""
        print("🚀 EJECUTANDO SUITE COMPLETA DE PRUEBAS\n")
        
        try:
            self.probar_conjuntos_predefinidos()
            self.probar_datos_generados()
            self.probar_parametros_opcionales()
            self.probar_casos_error()
            
        except KeyboardInterrupt:
            print("\n⏹️  Pruebas interrumpidas por el usuario")
        except Exception as e:
            print(f"\n💥 Error inesperado en suite de pruebas: {e}")
            traceback.print_exc()
        finally:
            self.generar_reporte_final()


def main():
    """Función principal del script de pruebas."""
    print("LinearidadTool - Script de Pruebas Automatizadas")
    print("=" * 50)
    
    # Verificar dependencias
    try:
        import numpy
        import matplotlib
        print(f"✅ NumPy: {numpy.__version__}")
        print(f"✅ Matplotlib: {matplotlib.__version__}")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        return 1
    
    # Ejecutar pruebas
    tester = TestLinealidadTool()
    tester.ejecutar_todas_las_pruebas()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
