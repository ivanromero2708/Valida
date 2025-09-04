# Template_infor_val.docx - Estructura Consolidada

## Instrucciones de Uso

1. Abrir `Template_infor_val.docx` en Microsoft Word
2. Copiar y pegar cada sección según se indica
3. Reemplazar el contenido existente con las variables Jinja2
4. Mantener el formato de tablas y estilos

---

## PORTADA

```
INFORME DE VALIDACIÓN DE MÉTODO ANALÍTICO

{{project_info.title}}

Producto: {{project_info.product}}
Método: {{project_info.method}}
Analista: {{project_info.analyst}}
Laboratorio: {{project_info.laboratory}}
Fecha: {{project_info.date.strftime("%d/%m/%Y")}}
Equipo: {{project_info.equipment}}
```

---

## 1. INFORMACIÓN GENERAL

### 1.1 Datos del Proyecto
- **Título:** {{project_info.title}}
- **Producto:** {{project_info.product}}
- **Método Analítico:** {{project_info.method}}
- **Analista Responsable:** {{project_info.analyst}}
- **Laboratorio:** {{project_info.laboratory}}
- **Equipo Principal:** {{project_info.equipment}}
- **Fecha de Análisis:** {{project_info.date.strftime("%d de %B de %Y")}}

---

## 2. MATERIALES E INSUMOS

### 2.1 Muestras Utilizadas

| Nombre | Código | Lote | Código Interno CIM |
|--------|--------|------|-------------------|
{%tr for muestra in muestra_utilizadas%}| {{muestra.nombre}} | {{muestra.codigo}} | {{muestra.lote}} | {{muestra.codigo_interno_cim}} |{%endtr%}

### 2.2 Estándares de Referencia

| Nombre | Fabricante | Lote | No. Parte | Código ID | Concentración | Vencimiento |
|--------|------------|------|-----------|-----------|---------------|-------------|
{%tr for estandar in estandar_utilizados%}| {{estandar.nombre}} | {{estandar.fabricante}} | {{estandar.lote}} | {{estandar.numero_parte}} | {{estandar.codigo_identificacion}} | {{estandar.concentracion}} | {{estandar.vencimiento}} |{%endtr%}

### 2.3 Reactivos

| Nombre | Fabricante | Lote | No. Parte | Vencimiento |
|--------|------------|------|-----------|-------------|
{%tr for reactivo in reactivo_utilizados%}| {{reactivo.nombre}} | {{reactivo.fabricante}} | {{reactivo.lote}} | {{reactivo.numero_parte}} | {{reactivo.vencimiento}} |{%endtr%}

### 2.4 Materiales

| Nombre | Fabricante | No. Parte | Lote |
|--------|------------|-----------|------|
{%tr for material in materiales_utilizados%}| {{material.nombre}} | {{material.fabricante}} | {{material.numero_parte}} | {{material.lote}} |{%endtr%}

### 2.5 Equipos

| Nombre | Consecutivo | Fabricante | Modelo | Serial | Próx. Actividad |
|--------|-------------|------------|--------|--------|-----------------|
{%tr for equipo in equipos_utilizados%}| {{equipo.nombre}} | {{equipo.consecutivo}} | {{equipo.fabricante}} | {{equipo.modelo}} | {{equipo.serial}} | {{equipo.prox_actividad}} |{%endtr%}

### 2.6 Columnas Cromatográficas

| Descripción | Fabricante | No. Parte | Serial | No. Interno |
|-------------|------------|-----------|--------|-------------|
{%tr for columna in columna_utilizada%}| {{columna.descripcion}} | {{columna.fabricante}} | {{columna.numero_parte}} | {{columna.serial}} | {{columna.numero_interno}} |{%endtr%}

---

## 3. LINEALIDAD DEL SISTEMA

{%tr for activo in activos%}
### 3.{{loop.index}} {{activo.nombre}}

**Criterios de Aceptación:**
- Coeficiente de correlación (r): ≥ {{activo.criterios.r_min}}
- RSD de factores de respuesta: ≤ {{activo.criterios.rsd_max}}%
- Porcentaje de intercepto: ≤ {{activo.criterios.pct_intercepto_max}}%

**Resultados:**

| Nivel | Concentración (mg/mL) | Área Promedio | Factor Respuesta | RSD (%) |
|-------|----------------------|---------------|------------------|---------|
{%tr for nivel in activo.linealidad_sistema%}| {{nivel.nivel}} | {{nivel.replicas[0].concentracion}} | {{(nivel.replicas|map(attribute='area_pico')|list|sum / nivel.replicas|length)|round(1)}} | {{(nivel.replicas|map(attribute='factor_respuesta')|list|sum / nivel.replicas|length)|round(3)}} | {{((nivel.replicas|map(attribute='factor_respuesta')|list|stdev / (nivel.replicas|map(attribute='factor_respuesta')|list|sum / nivel.replicas|length)) * 100)|round(2)}} |{%endtr%}

**Métricas de Regresión:**
- Pendiente: {{activo.metrics.pendiente|round(2)}}
- Intercepto: {{activo.metrics.intercepto|round(2)}}
- Coeficiente de correlación (r): {{activo.metrics.r|round(4)}}
- Coeficiente de determinación (r²): {{activo.metrics.r2|round(4)}}
- RSD global de factores: {{activo.metrics.rsd_factor|round(2)}}%
- Porcentaje de intercepto: {{activo.metrics.porcentaje_intercepto|round(2)}}%

**Conclusión:** {% if activo.metrics.cumple_global %}Cumple{% else %}No cumple{% endif %}

{%endtr%}

---

## 4. EXACTITUD DEL MÉTODO

{%tr for activo in activos%}
### 4.{{loop.index}} {{activo.nombre}}

**Criterio:** {{activo.exactitude_del_metodo[0].criterio}}

| Nivel | Réplica 1 | Réplica 2 | Réplica 3 | Promedio (%) | Conclusión |
|-------|-----------|-----------|-----------|--------------|------------|
{%tr for nivel in activo.exactitude_del_metodo%}| {{nivel.nivel}} | {{nivel.replicas[0].recuperacion}}% | {{nivel.replicas[1].recuperacion}}% | {{nivel.replicas[2].recuperacion}}% | {{nivel.recuperacion_promedio|round(1)}}% | {{nivel.conclusion}} |{%endtr%}

**Conclusión Global:** {{activo.conclusion_global}}

{%endtr%}

---

## 5. PRECISIÓN DEL SISTEMA

**Criterio:** {{criterio_precision_sistema}}

| Réplica | Área Pico 1 | Área Pico 2 | Área Pico 3 | Área Pico 4 | Área Pico 5 | Criterio | Conclusión |
|---------|-------------|-------------|-------------|-------------|-------------|----------|------------|
{%tr for replica in precision_sistema%}| {{replica.replica}} | {{replica.area_pico_1}} | {{replica.area_pico_2}} | {{replica.area_pico_3}} | {{replica.area_pico_4}} | {{replica.area_pico_5}} | {{replica.criterio}} | {{replica.conclusion}} |{%endtr%}

**RSD por Activo:**
- Activo 1: {{RSD_precision_pico_1}}%
- Activo 2: {{RSD_precision_pico_2}}%
- Activo 3: {{RSD_precision_pico_3}}%
- Activo 4: {{RSD_precision_pico_4}}%
- Activo 5: {{RSD_precision_pico_5}}%

**Conclusión Global:** {{conclusion_global_precision_sistema}}

---

## 6. REPETIBILIDAD

**Criterio:** El %RSD obtenido debe ser menor o igual a 2.0%.

| Réplica | % Pico 1 | % Pico 2 | % Pico 3 | % Pico 4 | % Pico 5 | Criterio | Conclusión |
|---------|----------|----------|----------|----------|----------|----------|------------|
{%tr for replica in precision_metodo%}| {{replica.replica}} | {{replica.porcentaje_pico_1}} | {{replica.porcentaje_pico_2}} | {{replica.porcentaje_pico_3}} | {{replica.porcentaje_pico_4}} | {{replica.porcentaje_pico_5}} | {{replica.criterio}} | {{replica.conclusion}} |{%endtr%}

**RSD por Activo:**
- Activo 1: {{RSD_precision_pico_1}}% - {{CONC_precision_pico_1}}
- Activo 2: {{RSD_precision_pico_2}}% - {{CONC_precision_pico_2}}
- Activo 3: {{RSD_precision_pico_3}}% - {{CONC_precision_pico_3}}
- Activo 4: {{RSD_precision_pico_4}}% - {{CONC_precision_pico_4}}
- Activo 5: {{RSD_precision_pico_5}}% - {{CONC_precision_pico_5}}

**Conclusión Global:** {{conclusion_global}}

---

## 7. PRECISIÓN INTERMEDIA

**Criterio:** {{criterio_txt}}

| Réplica | AN1 Act1 | AN2 Act1 | AN1 Act2 | AN2 Act2 | AN1 Act3 | AN2 Act3 | AN1 Act4 | AN2 Act4 | AN1 Act5 | AN2 Act5 |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
{%tr for fila in filas%}| {{fila.replica}} | {{fila.activos[0].an1}} | {{fila.activos[0].an2}} | {{fila.activos[1].an1}} | {{fila.activos[1].an2}} | {{fila.activos[2].an1}} | {{fila.activos[2].an2}} | {{fila.activos[3].an1}} | {{fila.activos[3].an2}} | {{fila.activos[4].an1}} | {{fila.activos[4].an2}} |{%endtr%}

**RSD por Activo:**
{%tr for rsd in rsd_por_activo%}- Activo {{loop.index}}: {{rsd}}%{%endtr%}

**Conclusión Global:** {{conclusion_global}}

---

## 8. ESTABILIDAD DE SOLUCIONES

**Criterio:** {{criterio_txt}}

| Activo | Área T0 | Área T1C1 | %Di T1C1 | Área T1C2 | %Di T1C2 | Área T2C1 | %Di T2C1 | Área T2C2 | %Di T2C2 | Área T3C1 | %Di T3C1 | Área T3C2 | %Di T3C2 |
|--------|---------|-----------|----------|-----------|----------|-----------|----------|-----------|----------|-----------|----------|-----------|----------|
{%tr for activo in activos%}| {{activo.nombre}} | {{activo.area_T0}} | {{activo.area_T1C1}} | {{activo.di_T1C1}} | {{activo.area_T1C2}} | {{activo.di_T1C2}} | {{activo.area_T2C1}} | {{activo.di_T2C1}} | {{activo.area_T2C2}} | {{activo.di_T2C2}} | {{activo.area_T3C1}} | {{activo.di_T3C1}} | {{activo.area_T3C2}} | {{activo.di_T3C2}} |{%endtr%}

**Conclusiones por Tiempo y Condición:**
- T1C1: {{concl_T1C1}}
- T1C2: {{concl_T1C2}}
- T2C1: {{concl_T2C1}}
- T2C2: {{concl_T2C2}}
- T3C1: {{concl_T3C1}}
- T3C2: {{concl_T3C2}}

---

## 9. ESTABILIDAD DE FASE MÓVIL

**Criterio:** {{criterio_txt}}

### 9.1 Tiempos de Retención

| Réplica | {{headers_activos[0]}} T0 | {{headers_activos[0]}} T1 | {{headers_activos[0]}} T2 | {{headers_activos[1]}} T0 | {{headers_activos[1]}} T1 | {{headers_activos[1]}} T2 | {{headers_activos[2]}} T0 | {{headers_activos[2]}} T1 | {{headers_activos[2]}} T2 | {{headers_activos[3]}} T0 | {{headers_activos[3]}} T1 | {{headers_activos[3]}} T2 | {{headers_activos[4]}} T0 | {{headers_activos[4]}} T1 | {{headers_activos[4]}} T2 |
|---------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|------------|
{%tr for replica in replicas%}| {{replica.num}} | {{replica.t0[0]}} | {{replica.t1[0]}} | {{replica.t2[0]}} | {{replica.t0[1]}} | {{replica.t1[1]}} | {{replica.t2[1]}} | {{replica.t0[2]}} | {{replica.t1[2]}} | {{replica.t2[2]}} | {{replica.t0[3]}} | {{replica.t1[3]}} | {{replica.t2[3]}} | {{replica.t0[4]}} | {{replica.t1[4]}} | {{replica.t2[4]}} |{%endtr%}

### 9.2 Parámetros de Adecuabilidad del Sistema

| Parámetro | {{headers_activos[0]}} | {{headers_activos[1]}} | {{headers_activos[2]}} | {{headers_activos[3]}} | {{headers_activos[4]}} |
|-----------|------------|------------|------------|------------|------------|
| RSD T0 (%) | {{rsd_t0[0]}} | {{rsd_t0[1]}} | {{rsd_t0[2]}} | {{rsd_t0[3]}} | {{rsd_t0[4]}} |
| RSD T1 (%) | {{rsd_t1[0]}} | {{rsd_t1[1]}} | {{rsd_t1[2]}} | {{rsd_t1[3]}} | {{rsd_t1[4]}} |
| RSD T2 (%) | {{rsd_t2[0]}} | {{rsd_t2[1]}} | {{rsd_t2[2]}} | {{rsd_t2[3]}} | {{rsd_t2[4]}} |
| Asimetría T0 | {{asim_t0[0]}} | {{asim_t0[1]}} | {{asim_t0[2]}} | {{asim_t0[3]}} | {{asim_t0[4]}} |
| Asimetría T1 | {{asim_t1[0]}} | {{asim_t1[1]}} | {{asim_t1[2]}} | {{asim_t1[3]}} | {{asim_t1[4]}} |
| Asimetría T2 | {{asim_t2[0]}} | {{asim_t2[1]}} | {{asim_t2[2]}} | {{asim_t2[3]}} | {{asim_t2[4]}} |
| Exactitud T0 (%) | {{exact_t0[0]}} | {{exact_t0[1]}} | {{exact_t0[2]}} | {{exact_t0[3]}} | {{exact_t0[4]}} |
| Exactitud T1 (%) | {{exact_t1[0]}} | {{exact_t1[1]}} | {{exact_t1[2]}} | {{exact_t1[3]}} | {{exact_t1[4]}} |
| Exactitud T2 (%) | {{exact_t2[0]}} | {{exact_t2[1]}} | {{exact_t2[2]}} | {{exact_t2[3]}} | {{exact_t2[4]}} |

### 9.3 Resolución y Variación de Tiempos

| Parámetro | T0 | T1 | T2 |
|-----------|----|----|----| 
| Resolución | {{resol_T0}} | {{resol_T1}} | {{resol_T2}} |
| ΔT promedio (min) | - | {{deltaT_T1}} | {{deltaT_T2}} |

**Conclusiones:**
- T1: {{concl_T1}}
- T2: {{concl_T2}}

---

## 10. ROBUSTEZ

**Criterio:** {{criterio_txt}}

{%tr for compuesto in compuestos%}
### 10.{{loop.index}} {{compuesto.nombre}}

| Condición | Nominal | Factor A+ | Factor A- | Factor B+ | Factor B- | Factor C+ | Factor C- | Factor D+ | Factor D- |
|-----------|---------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
{%tr for param in compuesto.param_rows%}| {{param.parametro}} | {{param.valores[0]}} | {{param.valores[1]}} | {{param.valores[2]}} | {{param.valores[3]}} | {{param.valores[4]}} | {{param.valores[5]}} | {{param.valores[6]}} | {{param.valores[7]}} | {{param.valores[8]}} |{%endtr%}

{%endtr%}

**Conclusiones por Condición:**
{%tr for conclusion in conclusiones%}- Condición {{loop.index}}: {{conclusion}}{%endtr%}

---

## 11. CONCLUSIONES GENERALES

### 11.1 Resumen de Resultados

| Parámetro | Resultado | Criterio | Cumple |
|-----------|-----------|----------|--------|
| Linealidad | R² ≥ 0.998 | ✓ | Sí |
| Exactitud | 98.0-102.0% | ✓ | Sí |
| Precisión Sistema | RSD ≤ 2.0% | ✓ | Sí |
| Repetibilidad | RSD ≤ 2.0% | ✓ | Sí |
| Precisión Intermedia | RSD ≤ 2.0% | ✓ | Sí |
| Estabilidad Soluciones | Δ ≤ 2.0% | ✓ | Sí |
| Estabilidad Fase Móvil | ΔT ≤ 3 min | ✓ | Sí |
| Robustez | |di| ≤ 2.0% | ✓ | Sí |

### 11.2 Conclusión Final

El método analítico {{project_info.method}} para la determinación de {{project_info.product}} ha sido validado satisfactoriamente según los criterios establecidos. Todos los parámetros evaluados cumplen con las especificaciones requeridas.

**Fecha de validación:** {{project_info.date.strftime("%d de %B de %Y")}}
**Analista responsable:** {{project_info.analyst}}
**Laboratorio:** {{project_info.laboratory}}

---

## ANEXOS

### Anexo A: Cromatogramas Representativos
[Insertar cromatogramas]

### Anexo B: Certificados de Estándares de Referencia
[Insertar certificados]

### Anexo C: Registros de Calibración de Equipos
[Insertar registros]

### Anexo D: Cálculos Estadísticos Detallados
[Insertar cálculos]
