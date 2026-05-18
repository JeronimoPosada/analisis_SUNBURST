# Análisis de Calidad de Datos - Rol 2

## Proyecto: Análisis de Gestión de Datos del Caso SUNBURST de SolarWinds
### Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

---

## 1. Marco Teórico: DAMA DMBOK

El **DAMA DMBOK** (Data Management Body of Knowledge) define la calidad de datos como el grado en que los datos satisfacen las necesidades establecidas. Para este análisis, se implementaron **3 dimensiones de calidad**:

| Dimensión | Definición DAMA | Fórmula Implementada |
|-----------|-----------------|---------------------|
| **Completitud** | Grado en que todos los valores requeridos están presentes | `(no_nulos / total) × 100` |
| **Exactitud** | Grado en que los datos representan correctamente la realidad | `(valores_válidos / total) × 100` |
| **Consistencia** | Grado en que los datos son coherentes entre sí | `(relaciones_válidas / total) × 100` |

---

## 2. Métricas Aplicadas y Resultados

### 2.1 Completitud (Umbral: ≥ 95%)

Se evaluó cada columna de cada tabla para verificar la ausencia de valores nulos.

**Resultado**: ✅ **100% de completitud** en todas las tablas y columnas.

Esto es esperable dado que los datos fueron generados sintéticamente con funciones que garantizan la presencia de todos los valores. En un escenario real, la completitud suele ser menor, especialmente en campos opcionales.

### 2.2 Exactitud (Umbral: ≥ 90%)

Se verificó que los valores estén dentro de los rangos y formatos esperados:
- **Strings**: No vacíos y con longitud razonable
- **IDs numéricos**: Valores positivos
- **Booleanos**: Valores válidos (`True`/`False`)
- **Categorías**: Dentro de los valores permitidos

**Resultado**: ✅ **100% de exactitud** en todas las validaciones.

### 2.3 Consistencia (Umbral: 100%)

Se validaron tres aspectos de consistencia:

1. **Integridad referencial `cliente_id`**: Todos los `cliente_id` en la tabla `instalaciones` existen en la tabla `clientes`.
   - **Resultado**: ✅ 100%

2. **Integridad referencial `version_id`**: Todos los `version_id` en la tabla `instalaciones` existen en la tabla `versiones_software`.
   - **Resultado**: ✅ 100%

3. **Coherencia temporal**: Todas las fechas de instalación son posteriores a las fechas de release de la versión correspondiente.
   - **Resultado**: ✅ 100%

### Resumen General

| Métrica | Evaluaciones | Aprobadas | Tasa |
|---------|-------------|-----------|------|
| Completitud | 16 columnas | 16 | 100% |
| Exactitud | 16 columnas | 16 | 100% |
| Consistencia | 3 relaciones | 3 | 100% |
| **Total** | **35** | **35** | **100%** |

---

## 3. Hallazgos de Calidad

### Fortalezas de los Datos
1. **Cero valores nulos** en todas las tablas
2. **Cero duplicados** en identificadores primarios
3. **Integridad referencial perfecta** entre tablas
4. **Coherencia temporal** completa

### Observaciones
1. Los datos sintéticos tienen calidad "perfecta", lo cual raramente ocurre en datos reales
2. En un escenario real, se esperarían problemas como:
   - Nombres de organizaciones con caracteres especiales o vacíos
   - Fechas faltantes o en formatos inconsistentes
   - IDs huérfanos (instalaciones apuntando a clientes eliminados)
3. La calidad perfecta nos permite enfocarnos en el **análisis de anomalías de seguridad**

---

## 4. Anomalías Detectadas

### 4.1 Eventos de Seguridad Generados

Se generaron **200 eventos de seguridad** simulando la actividad del malware SUNBURST:

| Categoría | Cantidad | Porcentaje |
|-----------|----------|------------|
| Eventos normales | ~187 | ~93.5% |
| Eventos anómalos | ~13 | ~6.5% |

### 4.2 Tipos de Eventos Anómalos

Los eventos anómalos se concentran en actividades maliciosas típicas de un APT (Advanced Persistent Threat):

| Tipo de Evento | Descripción | Relevancia al Caso |
|----------------|-------------|-------------------|
| `conexion_c2` | Conexión a servidor de comando y control | SUNBURST se comunicaba con servidores C2 para recibir instrucciones |
| `exfiltracion` | Extracción de datos | El objetivo final era robar información sensible |
| `escalamiento_privilegios` | Obtención de mayores permisos | Los atacantes escalaban privilegios para acceder a más recursos |
| `movimiento_lateral` | Desplazamiento a otros sistemas | Los atacantes se movían dentro de la red de la víctima |
| `modificacion_logs` | Alteración de registros | Los atacantes borraban su rastro |

### 4.3 Severidad de Anomalías

La distribución de severidad de eventos anómalos muestra un patrón coherente con ataques avanzados:
- **Crítica**: ~45% de los eventos anómalos
- **Alta**: ~40%
- **Media**: ~10%
- **Baja**: ~5%

Esto contrasta con los eventos normales donde la severidad es predominantemente Baja (50%) y Media (30%).

---

## 5. Análisis del Problema 18,000 vs <100

### El Filtrado en Cascada

Uno de los hallazgos más significativos del caso SUNBURST es la reducción dramática entre los clientes "afectados" inicialmente reportados y los realmente comprometidos:

| Etapa | Caso Real | Datos Sintéticos |
|-------|-----------|------------------|
| Total descargas activadas | 18,000 | 100 instalaciones |
| Con versiones SUNBURST | 18,000 | ~78 instalaciones |
| Con actividad maliciosa detectada | No publicado | ~72 con eventos |
| Realmente comprometidos | <100 | ~12 instalaciones |
| Clientes únicos comprometidos | ~9 entidades gob. | ~12 clientes |
| **Reducción total** | **>99.4%** | **~84.6%** |

### ¿Por qué la diferencia?

1. **No todas las instalaciones ejecutaban el malware**: Algunas organizaciones descargaron las versiones afectadas pero no las instalaron o las reemplazaron rápidamente
2. **SUNBURST tenía un período de latencia**: El malware esperaba ~2 semanas antes de activarse, filtrando organizaciones fuera de línea
3. **Los atacantes eran selectivos**: Solo explotaron activamente organizaciones de alto valor (gobierno, defensa, tecnología)
4. **El Hotfix 5 detuvo la propagación**: Las organizaciones que aplicaron el parche dejaron de estar expuestas

### Implicación para la Gestión de Datos

La comunicación inicial de "18,000 afectados" versus la cifra real de "<100" demuestra:
- La importancia de la **precisión en la comunicación de datos** durante crisis
- El costo reputacional de sobreestimar el impacto (como mencionó Ramakrishna: "Todavía veo '18,000 afectados' en los titulares")
- La necesidad de procesos de **filtrado y validación** antes de publicar cifras

---

## 6. Visualizaciones Generadas

Se crearon **5 gráficos** que visualizan los hallazgos:

| Gráfico | Archivo | Descripción |
|---------|---------|-------------|
| Anomalías | `anomalias.png` | Proporción de eventos anómalos vs normales + tipos de anomalías |
| Severidad | `severidad_eventos.png` | Distribución de severidad en eventos normales vs anómalos |
| Clientes | `clientes_afectados.png` | Criticidad y sectores de clientes |
| Calidad | `calidad_datos.png` | Heatmap de métricas DAMA por tabla/columna |
| Cascada | `grafico_cascada.png` | Filtrado progresivo de 18,000 a <100 |

---

## 7. Conclusiones

1. **La calidad de datos es fundamental en ciberseguridad**: El caso SUNBURST demuestra que datos mal gestionados pueden llevar a pánico innecesario o a pasar por alto amenazas reales.

2. **Las métricas DAMA proveen un marco estructurado**: Completitud, Exactitud y Consistencia son dimensiones mínimas que todo dataset debe cumplir antes de ser analizado.

3. **La detección de anomalías requiere contexto**: No basta con identificar valores atípicos estadísticamente; se necesita conocimiento del dominio (tipos de ataques, patrones de APT) para interpretar los hallazgos.

4. **La comunicación de datos en crisis es crítica**: La diferencia entre 18,000 y <100 muestra cómo una cifra mal contextualizada puede tener consecuencias reputacionales severas.
