# Analisis de Calidad de Datos - Rol 2

## Proyecto: Analisis de Gestion de Datos del Caso SUNBURST de SolarWinds
### Universidad de San Buenaventura | Gestion de Datos | 3er Semestre

---

## 1. Marco Teorico: DAMA DMBOK

El **DAMA DMBOK** define la calidad de datos como el grado en que los datos satisfacen las necesidades establecidas. Se implementaron 3 dimensiones:

| Dimension | Definicion | Formula | Umbral |
|-----------|-----------|---------|--------|
| **Completitud** | Campos completos (sin nulos ni vacios) | `(no_nulos / total) x 100` | >= 95% |
| **Exactitud** | Valores dentro de rangos validos | `(validos / total) x 100` | >= 90% |
| **Consistencia** | Coherencia entre tablas y relaciones | `(rel_validas / total) x 100` | = 100% |

---

## 2. Resultados: Metricas DAMA

### Resumen General

| Categoria | Total | Aprobadas | Fallidas | Tasa |
|-----------|-------|-----------|----------|------|
| Completitud | 16 | 15 | 1 | 93.7% |
| Exactitud | 16 | 15 | 1 | 93.7% |
| Consistencia | 7 | 1 | 6 | 14.3% |
| **TOTAL** | **39** | **31** | **8** | **79.5%** |

### Metricas Fallidas (detalle)

| Tabla | Columna | Metrica | Valor | Umbral | Deficit |
|-------|---------|---------|-------|--------|---------|
| clientes | nombre_organizacion | Completitud | 94.12% | 95% | -0.88% |
| versiones_software | fecha_release | Completitud | 87.5% | 95% | -7.5% |
| versiones_software | fecha_release | Exactitud | 87.5% | 90% | -2.5% |
| instalaciones | cliente_id (FK) | Consistencia | 98.0% | 100% | -2.0% |
| instalaciones | version_id (FK) | Consistencia | 99.0% | 100% | -1.0% |
| instalaciones | fecha >= release | Consistencia | 96.67% | 100% | -3.33% |
| instalaciones | rango 2019-2021 | Consistencia | 99.0% | 100% | -1.0% |
| clientes | cliente_id (unicidad) | Consistencia | 98.04% | 100% | -1.96% |

### Analisis Critico

El resultado de **79.5% de aprobacion** es significativo. Mientras que las metricas de Completitud y Exactitud tienen tasas aceptables (>93%), la **Consistencia solo alcanza 14.3%**. Esto revela que los problemas mas graves no estan en campos individuales sino en las **relaciones entre tablas**.

En un escenario de ciberseguridad como SUNBURST, una FK huerfana puede significar:
- Una instalacion comprometida que no se puede vincular a su organizacion
- Imposibilidad de notificar al cliente afectado
- Subestimacion o sobreestimacion del impacto real

---

## 3. Anomalias Detectadas en los Datos

### 3.1 Problemas Criticos (impactan directamente el analisis)

| ID | Problema | Tabla | Detalle | Impacto |
|----|---------|-------|---------|---------|
| C1 | FK huerfana: cliente_id | instalaciones | IDs 999, 888 no existen en clientes | Las instalaciones 11 y 68 no tienen organizacion asociada |
| C2 | FK huerfana: version_id | instalaciones | ID 99 no existe en versiones | La instalacion 36 no puede clasificarse como SUNBURST o limpia |
| C3 | Inconsistencia temporal | instalaciones | 3 fechas anteriores al release | Instalaciones 5, 20, 56 tienen fechas imposibles |
| C4 | Fecha fuera de rango | instalaciones | 2023-11-15 en fila 89 | Dato del futuro, fuera del periodo del caso |
| C5 | PK duplicada | clientes | cliente_id=12 aparece 2 veces | Ambiguedad en la identidad del cliente |

### 3.2 Problemas Altos (afectan la calidad pero no invalidan)

| ID | Problema | Tabla | Detalle | Impacto |
|----|---------|-------|---------|---------|
| A1 | Nulos en nombre_organizacion | clientes | 3 registros (filas 7, 23, 41) | Organizaciones sin identificar |
| A2 | Nulo en criticidad | clientes | 1 registro (fila 45) | No se puede clasificar el riesgo |
| A3 | Nulo en fecha_release | versiones | Version HF2 (ID=3) | No se puede verificar temporalidad |
| A4 | Nulos en nivel_datos_sensibles | instalaciones | 2 registros (filas 9, 73) | No se puede evaluar sensibilidad |

### 3.3 Problemas Medios (advertencias)

| ID | Problema | Tabla | Detalle | Impacto |
|----|---------|-------|---------|---------|
| M1 | Valor invalido tipo_org | clientes | 'Desconocido' (fila 28) | Categoria fuera de catalogo |
| M2 | Valor invalido nivel_sensibles | instalaciones | 'Desconocido' (fila 51) | Categoria fuera de catalogo |
| M3 | Paises vacios | clientes | 2 strings vacios (filas 15, 33) | Pais presente pero inutilizable |

### Total: 10 problemas criticos + 3 advertencias

---

## 4. Eventos de Seguridad

Se generaron **200 eventos de seguridad** simulando la actividad del malware:

| Categoria | Cantidad | Porcentaje |
|-----------|----------|------------|
| Eventos normales | ~188 | ~94% |
| Eventos anomalos | ~12 | ~6% |

### Tipos de eventos anomalos

Los eventos anomalos se concentran en actividades tipicas de APT:
- **conexion_c2**: Comunicacion con servidor de comando y control
- **exfiltracion**: Extraccion de datos sensibles
- **escalamiento_privilegios**: Obtencion de permisos elevados
- **movimiento_lateral**: Propagacion dentro de la red
- **modificacion_logs**: Eliminacion de evidencia

### Severidad anomala vs normal

| Severidad | Normales | Anomalos |
|-----------|---------|---------|
| Baja | ~50% | ~5% |
| Media | ~30% | ~10% |
| Alta | ~15% | ~40% |
| Critica | ~5% | ~45% |

Esta distribucion inversa es la clave: los eventos anomalos son predominantemente de severidad Alta/Critica.

---

## 5. Cascada 18,000 vs <100

| Etapa | Caso Real | Datos Sinteticos |
|-------|-----------|------------------|
| Total descargas | 18,000 | 100 instalaciones |
| Con SUNBURST | 18,000 | ~77 instalaciones |
| Con eventos | N/A | ~70 con eventos |
| Comprometidos | <100 | ~11 instalaciones |
| Clientes unicos | ~9 entidades | ~10 clientes |
| **Reduccion** | **>99.4%** | **~85.7%** |

---

## 6. Conclusiones Criticas

### Lo que un analisis superficial habria reportado
"100% de completitud, exactitud y consistencia. Los datos son perfectos."

### Lo que el analisis critico revelo
- **8 de 39 metricas FALLIDAS** (20.5% de fallo)
- **10 problemas criticos** incluyendo FK huerfanas e inconsistencias temporales
- **3 advertencias** sobre valores fuera de catalogo

### Lecciones para la Gestion de Datos

1. **Los datos nunca son perfectos**: Un reporte que dice 100% en todo es sospechoso.
2. **La consistencia es mas importante que la completitud**: Un campo nulo es molesto; una FK huerfana invalida toda una cadena de analisis.
3. **'Desconocido' es peor que NULL**: Un NULL es honesto; 'Desconocido' parece un dato real sin serlo.
4. **Las inconsistencias temporales destruyen la causalidad**: Si una instalacion parece anterior al software, todo el analisis temporal se compromete.
5. **La calidad de datos es critica en ciberseguridad**: En SUNBURST, la diferencia entre 18,000 y <100 depende de la precision de los datos.
