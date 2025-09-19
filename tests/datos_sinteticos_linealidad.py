"""
Generador de datos sintéticos para pruebas de linealidad
------------------------------------------------------
Genera diferentes conjuntos de datos para probar la herramienta de linealidad:
- Datos con linealidad perfecta
- Datos con ruido realista
- Datos con replicados por nivel
- Datos con diferentes rangos de concentración
- Casos extremos y de error
"""

import numpy as np
from typing import Dict, List, Tuple, Any
import random


class GeneradorDatosSinteticos:
    """Generador de conjuntos de datos sintéticos para análisis de linealidad."""
    
    def __init__(self, seed: int = 42):
        """
        Inicializa el generador con semilla para reproducibilidad.
        
        Args:
            seed: Semilla para generación aleatoria
        """
        np.random.seed(seed)
        random.seed(seed)
    
    def generar_linealidad_perfecta(
        self, 
        n_puntos: int = 6,
        conc_min: float = 0.1,
        conc_max: float = 1.0,
        pendiente: float = 1000.0,
        intercepto: float = 50.0
    ) -> Dict[str, List[float]]:
        """
        Genera datos con linealidad perfecta (R² = 1.0).
        
        Args:
            n_puntos: Número de puntos de calibración
            conc_min: Concentración mínima (mg/mL)
            conc_max: Concentración máxima (mg/mL)
            pendiente: Pendiente de la curva
            intercepto: Intercepto de la curva
            
        Returns:
            Dict con listas de concentración y área
        """
        concentraciones = np.linspace(conc_min, conc_max, n_puntos)
        areas = pendiente * concentraciones + intercepto
        
        return {
            "concentracion": concentraciones.tolist(),
            "area_pico": areas.tolist(),
            "descripcion": f"Linealidad perfecta: y = {pendiente}x + {intercepto}",
            "r2_esperado": 1.0
        }
    
    def generar_linealidad_con_ruido(
        self,
        n_puntos: int = 6,
        conc_min: float = 0.1,
        conc_max: float = 1.0,
        pendiente: float = 1000.0,
        intercepto: float = 50.0,
        ruido_pct: float = 2.0
    ) -> Dict[str, List[float]]:
        """
        Genera datos con ruido realista (R² ~ 0.995-0.999).
        
        Args:
            n_puntos: Número de puntos de calibración
            conc_min: Concentración mínima (mg/mL)
            conc_max: Concentración máxima (mg/mL)
            pendiente: Pendiente de la curva
            intercepto: Intercepto de la curva
            ruido_pct: Porcentaje de ruido a añadir
            
        Returns:
            Dict con listas de concentración y área
        """
        concentraciones = np.linspace(conc_min, conc_max, n_puntos)
        areas_teoricas = pendiente * concentraciones + intercepto
        
        # Añadir ruido gaussiano
        ruido = np.random.normal(0, ruido_pct/100 * areas_teoricas)
        areas_con_ruido = areas_teoricas + ruido
        
        # Asegurar valores positivos
        areas_con_ruido = np.maximum(areas_con_ruido, areas_teoricas * 0.1)
        
        return {
            "concentracion": concentraciones.tolist(),
            "area_pico": areas_con_ruido.tolist(),
            "descripcion": f"Linealidad con {ruido_pct}% ruido",
            "r2_esperado": 0.995
        }
    
    def generar_con_replicados(
        self,
        concentraciones_base: List[float] = [0.1, 0.3, 0.5, 0.7, 1.0],
        replicados_por_nivel: int = 3,
        pendiente: float = 1000.0,
        intercepto: float = 50.0,
        ruido_pct: float = 1.5
    ) -> Dict[str, List[float]]:
        """
        Genera datos con replicados por nivel de concentración.
        
        Args:
            concentraciones_base: Niveles de concentración únicos
            replicados_por_nivel: Número de replicados por nivel
            pendiente: Pendiente de la curva
            intercepto: Intercepto de la curva
            ruido_pct: Porcentaje de ruido
            
        Returns:
            Dict con listas de concentración y área
        """
        concentraciones = []
        areas = []
        
        for conc in concentraciones_base:
            for _ in range(replicados_por_nivel):
                area_teorica = pendiente * conc + intercepto
                ruido = np.random.normal(0, ruido_pct/100 * area_teorica)
                area_con_ruido = max(area_teorica + ruido, area_teorica * 0.1)
                
                concentraciones.append(conc)
                areas.append(area_con_ruido)
        
        return {
            "concentracion": concentraciones,
            "area_pico": areas,
            "descripcion": f"Datos con {replicados_por_nivel} replicados por nivel",
            "r2_esperado": 0.998
        }
    
    def generar_rango_amplio(
        self,
        n_puntos: int = 8,
        conc_min: float = 0.01,
        conc_max: float = 10.0,
        pendiente: float = 500.0,
        intercepto: float = 25.0,
        ruido_pct: float = 1.0
    ) -> Dict[str, List[float]]:
        """
        Genera datos con rango amplio de concentraciones.
        
        Args:
            n_puntos: Número de puntos
            conc_min: Concentración mínima
            conc_max: Concentración máxima
            pendiente: Pendiente de la curva
            intercepto: Intercepto de la curva
            ruido_pct: Porcentaje de ruido
            
        Returns:
            Dict con listas de concentración y área
        """
        # Distribución logarítmica para mejor cobertura del rango
        concentraciones = np.logspace(
            np.log10(conc_min), 
            np.log10(conc_max), 
            n_puntos
        )
        
        areas_teoricas = pendiente * concentraciones + intercepto
        ruido = np.random.normal(0, ruido_pct/100 * areas_teoricas)
        areas_con_ruido = np.maximum(areas_teoricas + ruido, areas_teoricas * 0.1)
        
        return {
            "concentracion": concentraciones.tolist(),
            "area_pico": areas_con_ruido.tolist(),
            "descripcion": f"Rango amplio: {conc_min}-{conc_max} mg/mL",
            "r2_esperado": 0.997
        }
    
    def generar_caso_farmaceutico_realista(self) -> Dict[str, List[float]]:
        """
        Genera un caso realista de validación farmacéutica.
        
        Simula una curva de calibración típica para un principio activo
        con 6 niveles de concentración y ligera variabilidad.
        
        Returns:
            Dict con datos realistas
        """
        # Concentraciones típicas para validación (80-120% del valor nominal)
        concentraciones = [0.08, 0.16, 0.20, 0.24, 0.28, 0.32]  # mg/mL
        
        # Parámetros realistas para HPLC
        pendiente = 2850.0  # Área/concentración típica
        intercepto = 125.0  # Ruido de fondo típico
        
        areas = []
        for conc in concentraciones:
            area_teorica = pendiente * conc + intercepto
            # Variabilidad típica en HPLC: 0.5-2%
            ruido = np.random.normal(0, 0.015 * area_teorica)
            area_final = max(area_teorica + ruido, area_teorica * 0.9)
            areas.append(area_final)
        
        return {
            "concentracion": concentraciones,
            "area_pico": areas,
            "descripcion": "Caso farmacéutico realista - Validación HPLC",
            "r2_esperado": 0.9995,
            "analito": "Principio Activo XYZ",
            "metodo": "HPLC-UV",
            "rango_validacion": "80-120% valor nominal"
        }


# Conjuntos de datos predefinidos para pruebas
CONJUNTOS_DATOS_PRUEBA = {
    "perfecto": {
        "concentracion": [0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
        "area_pico": [150.0, 250.0, 450.0, 650.0, 850.0, 1050.0],
        "descripcion": "Linealidad perfecta para pruebas básicas"
    },
    
    "con_ruido": {
        "concentracion": [0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
        "area_pico": [148.5, 252.1, 447.8, 653.2, 851.9, 1047.3],
        "descripcion": "Datos con ruido realista"
    },
    
    "farmaceutico": {
        "concentracion": [0.08, 0.16, 0.20, 0.24, 0.28, 0.32],
        "area_pico": [353.2, 581.4, 695.8, 809.1, 923.7, 1037.2],
        "descripcion": "Caso farmacéutico típico"
    },
    
    "con_replicados": {
        "concentracion": [0.2, 0.2, 0.2, 0.5, 0.5, 0.5, 0.8, 0.8, 0.8],
        "area_pico": [248.1, 251.9, 249.3, 548.7, 552.1, 547.8, 848.2, 851.7, 849.9],
        "descripcion": "Datos con replicados por nivel"
    }
}


def obtener_conjunto_datos(nombre: str) -> Dict[str, Any]:
    """
    Obtiene un conjunto de datos predefinido por nombre.
    
    Args:
        nombre: Nombre del conjunto ('perfecto', 'con_ruido', 'farmaceutico', 'con_replicados')
        
    Returns:
        Dict con datos del conjunto solicitado
        
    Raises:
        KeyError: Si el nombre no existe
    """
    if nombre not in CONJUNTOS_DATOS_PRUEBA:
        disponibles = list(CONJUNTOS_DATOS_PRUEBA.keys())
        raise KeyError(f"Conjunto '{nombre}' no disponible. Disponibles: {disponibles}")
    
    return CONJUNTOS_DATOS_PRUEBA[nombre].copy()


def generar_casos_error() -> Dict[str, Dict[str, Any]]:
    """
    Genera casos que deben producir errores para probar manejo de excepciones.
    
    Returns:
        Dict con diferentes casos de error
    """
    return {
        "listas_diferentes_longitud": {
            "concentracion": [0.1, 0.2, 0.3],
            "area_pico": [100.0, 200.0],
            "error_esperado": "Las listas deben tener la misma longitud"
        },
        
        "valores_negativos_concentracion": {
            "concentracion": [-0.1, 0.2, 0.3],
            "area_pico": [100.0, 200.0, 300.0],
            "error_esperado": "Valores deben ser positivos"
        },
        
        "valores_negativos_area": {
            "concentracion": [0.1, 0.2, 0.3],
            "area_pico": [100.0, -200.0, 300.0],
            "error_esperado": "Valores deben ser positivos"
        },
        
        "datos_insuficientes": {
            "concentracion": [0.1],
            "area_pico": [100.0],
            "error_esperado": "Mínimo 2 puntos requeridos"
        },
        
        "listas_vacias": {
            "concentracion": [],
            "area_pico": [],
            "error_esperado": "Listas no pueden estar vacías"
        }
    }


if __name__ == "__main__":
    # Ejemplo de uso del generador
    generador = GeneradorDatosSinteticos()
    
    print("=== CONJUNTOS DE DATOS SINTÉTICOS ===\n")
    
    # Generar diferentes tipos de datos
    datos_perfectos = generador.generar_linealidad_perfecta()
    print(f"1. {datos_perfectos['descripcion']}")
    print(f"   Concentraciones: {datos_perfectos['concentracion']}")
    print(f"   Áreas: {[round(x, 1) for x in datos_perfectos['area_pico']]}\n")
    
    datos_ruido = generador.generar_linealidad_con_ruido()
    print(f"2. {datos_ruido['descripcion']}")
    print(f"   R² esperado: {datos_ruido['r2_esperado']}\n")
    
    datos_replicados = generador.generar_con_replicados()
    print(f"3. {datos_replicados['descripcion']}")
    print(f"   Total de puntos: {len(datos_replicados['concentracion'])}\n")
    
    datos_farmaceuticos = generador.generar_caso_farmaceutico_realista()
    print(f"4. {datos_farmaceuticos['descripcion']}")
    print(f"   Analito: {datos_farmaceuticos['analito']}")
    print(f"   Método: {datos_farmaceuticos['metodo']}\n")
    
    print("=== CONJUNTOS PREDEFINIDOS ===")
    for nombre in CONJUNTOS_DATOS_PRUEBA:
        datos = obtener_conjunto_datos(nombre)
        print(f"- {nombre}: {datos['descripcion']}")
