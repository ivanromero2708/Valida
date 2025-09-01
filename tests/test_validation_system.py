# -*- coding: utf-8 -*-
"""
Prueba del sistema de validación consolidado.
Demuestra el uso de los modelos Pydantic y el nodo de renderizado.
"""

from datetime import datetime
from pathlib import Path

from src.models.validation_data import (
    ValidationRequest,
    ProjectInfo,
    LinearityRequest,
    LinearityData,
    LinearityLevel,
    AccuracyRequest,
    AccuracyData,
    AccuracyLevel,
    MaterialsData,
    SampleInfo,
    StandardInfo,
    ReagentInfo,
    MaterialInfo,
    EquipmentInfo,
    ColumnInfo,
    SystemPrecisionRequest,
    SystemPrecisionData,
)
from src.graph.nodes.render_validation_report import generate_validation_report


def create_demo_validation_request() -> ValidationRequest:
    """Crea una solicitud de validación de demostración."""
    
    # Información del proyecto
    project_info = ProjectInfo(
        title="Validación Método HPLC - Cafeína y Ácido Ascórbico",
        product="Tabletas Multivitamínicas XYZ",
        analyst="Dr. Juan Pérez",
        method="HPLC-UV Fase Reversa",
        laboratory="Laboratorio de Control de Calidad",
        equipment="HPLC Agilent 1260 Infinity"
    )
    
    # Datos de linealidad
    linearity_data = LinearityRequest(
        activos=[
            LinearityData(
                nombre="Cafeína",
                linealidad_sistema=[
                    LinearityLevel(
                        nivel=1,
                        replicas=[
                            {"concentracion": 0.1000, "area_pico": 1230.5, "factor_respuesta": 12.35},
                            {"concentracion": 0.1000, "area_pico": 1228.1, "factor_respuesta": 12.32},
                            {"concentracion": 0.1000, "area_pico": 1236.9, "factor_respuesta": 12.38},
                        ]
                    ),
                    LinearityLevel(
                        nivel=2,
                        replicas=[
                            {"concentracion": 0.2000, "area_pico": 2451.2, "factor_respuesta": 12.26},
                            {"concentracion": 0.2000, "area_pico": 2460.3, "factor_respuesta": 12.30},
                            {"concentracion": 0.2000, "area_pico": 2448.7, "factor_respuesta": 12.24},
                        ]
                    ),
                    LinearityLevel(
                        nivel=3,
                        replicas=[
                            {"concentracion": 0.3000, "area_pico": 3665.4, "factor_respuesta": 12.21},
                            {"concentracion": 0.3000, "area_pico": 3659.8, "factor_respuesta": 12.20},
                            {"concentracion": 0.3000, "area_pico": 3671.2, "factor_respuesta": 12.24},
                        ]
                    ),
                    LinearityLevel(
                        nivel=4,
                        replicas=[
                            {"concentracion": 0.4000, "area_pico": 4890.1, "factor_respuesta": 12.23},
                            {"concentracion": 0.4000, "area_pico": 4902.6, "factor_respuesta": 12.26},
                            {"concentracion": 0.4000, "area_pico": 4881.7, "factor_respuesta": 12.20},
                        ]
                    ),
                    LinearityLevel(
                        nivel=5,
                        replicas=[
                            {"concentracion": 0.5000, "area_pico": 6123.0, "factor_respuesta": 12.25},
                            {"concentracion": 0.5000, "area_pico": 6132.5, "factor_respuesta": 12.27},
                            {"concentracion": 0.5000, "area_pico": 6111.9, "factor_respuesta": 12.22},
                        ]
                    ),
                ],
                criterios={
                    "r_min": 0.998,
                    "rsd_max": 2.0,
                    "pct_intercepto_max": 2.0,
                    "x_ref_100pct": 0.3000,
                }
            ),
            LinearityData(
                nombre="Ácido Ascórbico",
                linealidad_sistema=[
                    LinearityLevel(
                        nivel=1,
                        replicas=[
                            {"concentracion": 0.0500, "area_pico": 615.2, "factor_respuesta": 12.30},
                            {"concentracion": 0.0500, "area_pico": 614.1, "factor_respuesta": 12.28},
                            {"concentracion": 0.0500, "area_pico": 618.4, "factor_respuesta": 12.37},
                        ]
                    ),
                    LinearityLevel(
                        nivel=2,
                        replicas=[
                            {"concentracion": 0.1000, "area_pico": 1225.6, "factor_respuesta": 12.26},
                            {"concentracion": 0.1000, "area_pico": 1230.1, "factor_respuesta": 12.30},
                            {"concentracion": 0.1000, "area_pico": 1224.4, "factor_respuesta": 12.24},
                        ]
                    ),
                    LinearityLevel(
                        nivel=3,
                        replicas=[
                            {"concentracion": 0.1500, "area_pico": 1832.7, "factor_respuesta": 12.22},
                            {"concentracion": 0.1500, "area_pico": 1829.9, "factor_respuesta": 12.20},
                            {"concentracion": 0.1500, "area_pico": 1835.6, "factor_respuesta": 12.24},
                        ]
                    ),
                    LinearityLevel(
                        nivel=4,
                        replicas=[
                            {"concentracion": 0.2000, "area_pico": 2445.1, "factor_respuesta": 12.23},
                            {"concentracion": 0.2000, "area_pico": 2451.3, "factor_respuesta": 12.26},
                            {"concentracion": 0.2000, "area_pico": 2440.8, "factor_respuesta": 12.20},
                        ]
                    ),
                    LinearityLevel(
                        nivel=5,
                        replicas=[
                            {"concentracion": 0.2500, "area_pico": 3061.5, "factor_respuesta": 12.25},
                            {"concentracion": 0.2500, "area_pico": 3066.3, "factor_respuesta": 12.27},
                            {"concentracion": 0.2500, "area_pico": 3055.9, "factor_respuesta": 12.22},
                        ]
                    ),
                ]
            ),
        ]
    )
    
    # Datos de exactitud
    accuracy_data = AccuracyRequest(
        activos=[
            AccuracyData(
                nombre="Cafeína",
                niveles=[
                    AccuracyLevel(nivel="80%", replicas=[98.3, 99.1, 97.9]),
                    AccuracyLevel(nivel="100%", replicas=[100.2, 99.8, 100.4]),
                    AccuracyLevel(nivel="120%", replicas=[101.4, 101.9, 100.7]),
                ],
                rango_aceptacion=(98.0, 102.0)
            ),
            AccuracyData(
                nombre="Ácido Ascórbico",
                niveles=[
                    AccuracyLevel(nivel="80%", replicas=[97.8, 98.1, 98.4]),
                    AccuracyLevel(nivel="100%", replicas=[99.9, 100.0, 100.2]),
                    AccuracyLevel(nivel="120%", replicas=[101.5, 102.1, 101.9]),
                ]
            ),
        ]
    )
    
    # Datos de materiales
    materials_data = MaterialsData(
        muestra_utilizadas=[
            SampleInfo(
                nombre="Tabletas Multivitamínicas Lote A",
                codigo="TMV-A",
                lote="L2024-001",
                codigo_interno_cim="CIM-TMV-001"
            ),
            SampleInfo(
                nombre="Tabletas Multivitamínicas Lote B",
                codigo="TMV-B",
                lote="L2024-002",
                codigo_interno_cim="CIM-TMV-002"
            ),
        ],
        estandar_utilizados=[
            StandardInfo(
                nombre="USP Caffeine RS",
                fabricante="USP",
                lote="R1234567",
                numero_parte="1232015-CAF",
                codigo_identificacion="USP-CAF-RS-2024",
                concentracion="1000 µg/mL",
                vencimiento="2026-12-31"
            ),
            StandardInfo(
                nombre="Ascorbic Acid CRS",
                fabricante="Ph.Eur.",
                lote="C5678901",
                numero_parte="AA-CRS-2024",
                codigo_identificacion="EP-AA-CRS-2024",
                concentracion="500 µg/mL",
                vencimiento="2027-06-30"
            ),
        ],
        reactivo_utilizados=[
            ReagentInfo(
                nombre="Metanol LC-MS Grade",
                fabricante="Merck KGaA",
                lote="M2024-07-001",
                numero_parte="1.06007.2500",
                vencimiento="2027-07-01"
            ),
            ReagentInfo(
                nombre="Acetonitrilo HPLC Grade",
                fabricante="J.T.Baker",
                lote="ACN-2025-01-B",
                numero_parte="9829-03",
                vencimiento="2028-01-15"
            ),
            ReagentInfo(
                nombre="Ácido Fosfórico 85%",
                fabricante="Sigma-Aldrich",
                lote="H3PO4-2024-03",
                numero_parte="695017-500ML",
                vencimiento="2029-03-20"
            ),
        ],
        materiales_utilizados=[
            MaterialInfo(
                nombre="Filtro PTFE 0.22 µm",
                fabricante="Millipore",
                numero_parte="SLGV033RS",
                lote="F2025-02-A"
            ),
            MaterialInfo(
                nombre="Vial ámbar 2 mL con tapa",
                fabricante="Agilent Technologies",
                numero_parte="5182-0715",
                lote="V2024-12-C"
            ),
            MaterialInfo(
                nombre="Jeringa 1 mL",
                fabricante="BD",
                numero_parte="309628",
                lote="SYR-2024-11"
            ),
        ],
        equipos_utilizados=[
            EquipmentInfo(
                nombre="HPLC 1260 Infinity II",
                consecutivo="EQ-HPLC-001",
                fabricante="Agilent Technologies",
                modelo="G7111B",
                serial="US12345678901",
                prox_actividad="2026-11-15"
            ),
            EquipmentInfo(
                nombre="Balanza Analítica",
                consecutivo="EQ-BAL-003",
                fabricante="Mettler Toledo",
                modelo="XS205",
                serial="MT987654321098",
                prox_actividad="2026-09-20"
            ),
            EquipmentInfo(
                nombre="Ultrasonido",
                consecutivo="EQ-US-002",
                fabricante="Branson",
                modelo="5800",
                serial="BR456789012",
                prox_actividad="2026-08-10"
            ),
        ],
        columna_utilizada=[
            ColumnInfo(
                descripcion="C18, 150×4.6 mm, 5 µm",
                fabricante="Waters Corporation",
                numero_parte="WAT054275",
                serial="CL-2024-001-A",
                numero_interno="COL-C18-045"
            ),
        ]
    )
    
    # Datos de precisión del sistema
    system_precision_data = SystemPrecisionRequest(
        activos=[
            SystemPrecisionData(
                nombre="Cafeína",
                areas=[3115.0, 3120.1, 3118.2, 3116.9, 3110.2, 3119.7]
            ),
            SystemPrecisionData(
                nombre="Ácido Ascórbico",
                areas=[1944.0, 1946.9, 1943.9, 1945.2, 1945.1, 1944.1]
            ),
        ],
        umbral_rsd=2.0,
        criterio="El %RSD de 6 inyecciones replicadas de la solución estándar debe ser ≤ 2.0%."
    )
    
    # Crear solicitud completa
    validation_request = ValidationRequest(
        project_info=project_info,
        linearity_data=linearity_data,
        accuracy_data=accuracy_data,
        materials_data=materials_data,
        system_precision_data=system_precision_data,
        output_path="./tmp_files/validation_report_demo.docx"
    )
    
    return validation_request


def test_validation_system():
    """Prueba el sistema completo de validación."""
    print("=== Prueba del Sistema de Validación ===\n")
    
    try:
        # Crear solicitud de validación
        print("1. Creando solicitud de validación...")
        validation_request = create_demo_validation_request()
        print(f"   ✓ Solicitud creada para: {validation_request.project_info.title}")
        print(f"   ✓ Producto: {validation_request.project_info.product}")
        print(f"   ✓ Analista: {validation_request.project_info.analyst}")
        
        # Generar informe
        print("\n2. Generando informe de validación...")
        response = generate_validation_report(validation_request)
        
        # Mostrar resultados
        print(f"\n3. Resultados:")
        print(f"   ✓ Éxito: {response.success}")
        print(f"   ✓ Tiempo de procesamiento: {response.processing_time:.2f} segundos")
        print(f"   ✓ Secciones procesadas: {', '.join(response.sections_processed)}")
        
        if response.output_file:
            print(f"   ✓ Archivo generado: {response.output_file}")
            
        if response.errors:
            print(f"   ⚠ Errores ({len(response.errors)}):")
            for error in response.errors:
                print(f"     - {error}")
                
        if response.warnings:
            print(f"   ⚠ Advertencias ({len(response.warnings)}):")
            for warning in response.warnings:
                print(f"     - {warning}")
        
        # Metadatos
        print(f"\n4. Metadatos:")
        print(f"   - Plantilla utilizada: {response.metadata.get('template_used', 'N/A')}")
        print(f"   - Secciones solicitadas: {', '.join(response.metadata.get('sections_requested', []))}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        return None


def test_individual_sections():
    """Prueba secciones individuales del sistema."""
    print("\n=== Prueba de Secciones Individuales ===\n")
    
    from src.graph.nodes.render_validation_report import (
        LinearityProcessor,
        AccuracyProcessor,
        MaterialsProcessor,
        SystemPrecisionProcessor
    )
    
    # Crear datos de prueba simples
    validation_request = create_demo_validation_request()
    
    try:
        # Probar procesador de linealidad
        print("1. Probando procesador de linealidad...")
        linearity_result = LinearityProcessor.process(
            validation_request.linearity_data,
            validation_request.linearity_data.criterios_por_defecto
        )
        print(f"   ✓ Activos procesados: {len(linearity_result['activos'])}")
        for activo in linearity_result['activos']:
            print(f"     - {activo['nombre']}: R² = {activo['metrics']['r2']:.4f}")
        
        # Probar procesador de exactitud
        print("\n2. Probando procesador de exactitud...")
        accuracy_result = AccuracyProcessor.process(
            validation_request.accuracy_data,
            validation_request.accuracy_data.rango_aceptacion_por_defecto
        )
        print(f"   ✓ Activos procesados: {len(accuracy_result['activos'])}")
        for activo in accuracy_result['activos']:
            print(f"     - {activo['nombre']}: {activo['conclusion_global']}")
        
        # Probar procesador de materiales
        print("\n3. Probando procesador de materiales...")
        materials_result = MaterialsProcessor.process(validation_request.materials_data)
        print(f"   ✓ Muestras: {len(materials_result['muestra_utilizadas'])}")
        print(f"   ✓ Estándares: {len(materials_result['estandar_utilizados'])}")
        print(f"   ✓ Reactivos: {len(materials_result['reactivo_utilizados'])}")
        print(f"   ✓ Equipos: {len(materials_result['equipos_utilizados'])}")
        
        # Probar procesador de precisión del sistema
        print("\n4. Probando procesador de precisión del sistema...")
        precision_result = SystemPrecisionProcessor.process(validation_request.system_precision_data)
        print(f"   ✓ Conclusión: {precision_result['conclusion_global_precision_sistema']}")
        print(f"   ✓ Réplicas procesadas: {len(precision_result['precision_sistema'])}")
        
        print("\n✅ Todas las secciones procesadas correctamente")
        
    except Exception as e:
        print(f"❌ Error en prueba de secciones: {str(e)}")


if __name__ == "__main__":
    # Ejecutar pruebas
    print("Iniciando pruebas del sistema de validación...\n")
    
    # Prueba completa del sistema
    response = test_validation_system()
    
    # Prueba de secciones individuales
    test_individual_sections()
    
    print(f"\n{'='*50}")
    print("Pruebas completadas.")
    
    if response and response.success:
        print("✅ Sistema funcionando correctamente")
        if response.output_file and Path(response.output_file).exists():
            print(f"📄 Revisa el archivo generado: {response.output_file}")
    else:
        print("❌ Se encontraron problemas en el sistema")
        
    print(f"{'='*50}")
