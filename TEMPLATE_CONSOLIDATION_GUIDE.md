# Guía de Consolidación de Plantillas DOCX

## 📋 Objetivo

Consolidar todas las plantillas DOCX individuales en `src/templates/` en un único archivo `Template_infor_val.docx` que contenga todas las secciones de validación.

## 📁 Plantillas Actuales

Las siguientes plantillas deben consolidarse:

1. **Template_infor_val.docx** - Plantilla principal (base)
2. **linealidad_multi_activos_tr.docx** - Linealidad del sistema
3. **exactitud_multi.docx** - Exactitud del método
4. **materiales.docx** - Materiales e insumos
5. **template_precision.docx** - Precisión del sistema
6. **template_repetibilidad.docx** - Repetibilidad
7. **template_precision_intermedia_tr.docx** - Precisión intermedia
8. **estabilidad_tabla_tr.docx** - Estabilidad de soluciones
9. **fase_movil_tabla_tr.docx** - Estabilidad de fase móvil
10. **factores_robustez_template.docx** - Robustez

## 🔧 Proceso de Consolidación

### Paso 1: Análisis de Variables de Plantilla

Cada plantilla utiliza variables específicas que deben integrarse en la plantilla principal:

#### Linealidad
```
Variables: {{activos}}, {{activos.nombre}}, {{activos.linealidad_sistema}}, {{activos.metrics}}
Tablas: Tabla con columnas dinámicas por activo
```

#### Exactitud
```
Variables: {{activos}}, {{activos.exactitude_del_metodo}}, {{activos.conclusion_global}}
Tablas: Tabla de recuperación por niveles
```

#### Materiales
```
Variables: {{muestra_utilizadas}}, {{estandar_utilizados}}, {{reactivo_utilizados}}, 
          {{materiales_utilizados}}, {{equipos_utilizados}}, {{columna_utilizada}}
Tablas: Múltiples tablas de inventario
```

#### Precisión del Sistema
```
Variables: {{precision_sistema}}, {{RSD_precision_pico_1}} a {{RSD_precision_pico_5}}
Tablas: Tabla con columnas podables por número de activos
```

#### Repetibilidad
```
Variables: {{precision_metodo}}, {{RSD_precision_pico_1}} a {{RSD_precision_pico_5}},
          {{CONC_precision_pico_1}} a {{CONC_precision_pico_5}}
Tablas: Tabla con columnas podables
```

#### Precisión Intermedia
```
Variables: {{filas}}, {{rsd_por_activo}}, {{conclusion_global}}
Tablas: Tabla con gridSpan para manejo de columnas
```

#### Estabilidad de Soluciones
```
Variables: {{activos}}, {{concl_T1C1}}, {{concl_T1C2}}, {{concl_T2C1}}, 
          {{concl_T2C2}}, {{concl_T3C1}}, {{concl_T3C2}}
Tablas: Tabla de estabilidad temporal
```

#### Estabilidad de Fase Móvil
```
Variables: {{headers_activos}}, {{replicas}}, {{rsd_t0}}, {{rsd_t1}}, {{rsd_t2}},
          {{asim_t0}}, {{asim_t1}}, {{asim_t2}}, {{exact_t0}}, {{exact_t1}}, {{exact_t2}}
Tablas: Tabla compleja con múltiples tiempos
```

#### Robustez
```
Variables: {{compuestos}}, {{criterio_txt}}, {{conclusiones}}
Tablas: Tabla de factores de robustez
```

### Paso 2: Estructura del Template Consolidado

El `Template_infor_val.docx` consolidado debe tener la siguiente estructura:

```
1. PORTADA
   - {{project_info.title}}
   - {{project_info.product}}
   - {{project_info.analyst}}
   - {{project_info.date}}

2. INFORMACIÓN GENERAL
   - {{project_info.method}}
   - {{project_info.laboratory}}
   - {{project_info.equipment}}

3. MATERIALES E INSUMOS
   - Muestras: {%tr for muestra in muestra_utilizadas%}
   - Estándares: {%tr for estandar in estandar_utilizados%}
   - Reactivos: {%tr for reactivo in reactivo_utilizados%}
   - Materiales: {%tr for material in materiales_utilizados%}
   - Equipos: {%tr for equipo in equipos_utilizados%}
   - Columnas: {%tr for columna in columna_utilizada%}

4. LINEALIDAD DEL SISTEMA
   - {%tr for activo in activos%}
   - Tabla de niveles y réplicas
   - Métricas de regresión

5. EXACTITUD DEL MÉTODO
   - {%tr for activo in activos%}
   - Tabla de recuperación por niveles
   - Conclusiones por activo

6. PRECISIÓN DEL SISTEMA
   - Tabla: {{precision_sistema}}
   - RSD por activo: {{RSD_precision_pico_1}} ... {{RSD_precision_pico_5}}
   - Conclusión: {{conclusion_global_precision_sistema}}

7. REPETIBILIDAD
   - Tabla: {{precision_metodo}}
   - RSD: {{RSD_precision_pico_1}} ... {{RSD_precision_pico_5}}
   - Conclusiones: {{CONC_precision_pico_1}} ... {{CONC_precision_pico_5}}

8. PRECISIÓN INTERMEDIA
   - Tabla: {{filas}}
   - RSD por activo: {{rsd_por_activo}}
   - Conclusión: {{conclusion_global}}

9. ESTABILIDAD DE SOLUCIONES
   - Tabla: {%tr for activo in activos%}
   - Conclusiones: {{concl_T1C1}}, {{concl_T1C2}}, etc.

10. ESTABILIDAD DE FASE MÓVIL
    - Headers: {{headers_activos}}
    - Réplicas: {{replicas}}
    - Parámetros por tiempo: RSD, Asimetría, Exactitud

11. ROBUSTEZ
    - {%tr for compuesto in compuestos%}
    - Parámetros evaluados
    - Conclusiones por condición
```

### Paso 3: Implementación Manual

**Herramientas necesarias:**
- Microsoft Word
- Conocimiento de sintaxis Jinja2 para docxtpl

**Proceso:**

1. **Abrir Template_infor_val.docx** como base
2. **Copiar secciones** de cada plantilla individual
3. **Integrar variables** según el mapeo definido
4. **Ajustar tablas** para soportar datos dinámicos
5. **Probar renderizado** con datos de ejemplo

### Paso 4: Variables de Contexto Unificadas

El contexto final debe incluir todas las variables:

```python
context = {
    "project_info": {...},
    "activos": [...],  # Para linealidad y exactitud
    "muestra_utilizadas": [...],
    "estandar_utilizados": [...],
    "reactivo_utilizados": [...],
    "materiales_utilizados": [...],
    "equipos_utilizados": [...],
    "columna_utilizada": [...],
    "precision_sistema": [...],
    "RSD_precision_pico_1": "...",
    # ... más variables RSD
    "precision_metodo": [...],
    "CONC_precision_pico_1": "...",
    # ... más variables CONC
    "filas": [...],  # Precisión intermedia
    "rsd_por_activo": [...],
    "headers_activos": [...],  # Fase móvil
    "replicas": [...],
    "rsd_t0": [...],
    # ... más variables de fase móvil
    "compuestos": [...],  # Robustez
    "criterio_txt": "...",
    "conclusiones": [...]
}
```

## 🧪 Validación

Después de consolidar la plantilla:

1. **Ejecutar prueba:**
```bash
python tests/test_validation_system.py
```

2. **Verificar secciones** en el documento generado
3. **Comprobar formato** y estructura
4. **Validar datos** en tablas

## 📝 Notas Importantes

- **Backup:** Hacer copia de seguridad de plantillas originales
- **Iterativo:** Consolidar sección por sección
- **Testing:** Probar cada sección después de integrarla
- **Variables:** Mantener consistencia en nombres de variables
- **Tablas:** Considerar poda de columnas para tablas dinámicas

## 🔍 Troubleshooting

### Problema: Variables no encontradas
**Solución:** Verificar nombres exactos en el código Python

### Problema: Tablas mal formateadas
**Solución:** Revisar sintaxis {%tr%} y estructura de datos

### Problema: Columnas extra
**Solución:** Implementar lógica de poda en post-procesamiento

### Problema: Datos faltantes
**Solución:** Verificar que todos los procesadores generen las variables esperadas

## ✅ Checklist de Consolidación

- [ ] Analizar todas las plantillas individuales
- [ ] Mapear variables de cada sección
- [ ] Crear estructura base en Template_infor_val.docx
- [ ] Integrar sección de materiales
- [ ] Integrar sección de linealidad
- [ ] Integrar sección de exactitud
- [ ] Integrar sección de precisión del sistema
- [ ] Integrar sección de repetibilidad
- [ ] Integrar sección de precisión intermedia
- [ ] Integrar sección de estabilidad de soluciones
- [ ] Integrar sección de estabilidad de fase móvil
- [ ] Integrar sección de robustez
- [ ] Probar renderizado completo
- [ ] Validar formato y contenido
- [ ] Documentar cambios realizados

---

**Nota:** Esta consolidación requiere trabajo manual en Microsoft Word para integrar correctamente todas las secciones y sus variables correspondientes.
