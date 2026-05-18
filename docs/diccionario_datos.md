# Diccionario de Datos - Caso SUNBURST

## Proyecto: Análisis de Gestión de Datos del Caso SUNBURST de SolarWinds
### Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

---

## 1. Tabla: `clientes` (50 registros)

Representa las organizaciones que usaban la Plataforma Orion de SolarWinds.

| Columna | Tipo | Descripción | Valores Posibles | Ejemplo |
|---------|------|-------------|------------------|---------|
| `cliente_id` | int | Identificador único del cliente | 1-50 | `1` |
| `nombre_organizacion` | str | Nombre ficticio de la organización | Texto libre | `"TechCorp Solutions"` |
| `tipo_org` | str | Tipo/categoría de la organización | `Gobierno Federal`, `Gobierno Estatal`, `Empresa Privada`, `Institución Educativa`, `Organización de Salud`, `ONG` | `"Empresa Privada"` |
| `pais` | str | País donde opera la organización | `Estados Unidos`, `Reino Unido`, `Canadá`, `Alemania`, `Israel`, `Australia`, `Francia`, `Japón` | `"Estados Unidos"` |
| `sector` | str | Sector de la industria al que pertenece | `Tecnología`, `Defensa`, `Energía`, `Finanzas`, `Telecomunicaciones`, `Salud`, `Gobierno`, `Educación` | `"Tecnología"` |
| `criticidad` | str | Nivel de criticidad de la organización para la seguridad | `Alta`, `Media`, `Baja` | `"Alta"` |

**Clave primaria**: `cliente_id`
**Relaciones**: Referenciada por `instalaciones.cliente_id`

---

## 2. Tabla: `versiones_software` (8 registros)

Contiene las versiones de la Plataforma Orion de SolarWinds relevantes al caso SUNBURST.

| Columna | Tipo | Descripción | Valores Posibles | Ejemplo |
|---------|------|-------------|------------------|---------|
| `version_id` | int | Identificador único de la versión | 1-8 | `1` |
| `nombre_version` | str | Nombre oficial de la versión | Texto libre (basado en versiones reales) | `"Orion Platform 2019.4"` |
| `fecha_release` | date | Fecha de lanzamiento de la versión | 2019-10-22 a 2020-12-15 | `"2019-10-22"` |
| `contiene_sunburst` | bool | Indica si la versión contiene el malware SUNBURST | `True`, `False` | `True` |
| `fecha_compilacion` | date | Fecha en que se compiló el software | Anterior a `fecha_release` | `"2019-10-10"` |

**Clave primaria**: `version_id`
**Relaciones**: Referenciada por `instalaciones.version_id`

### Detalle de Versiones

| ID | Versión | Contiene SUNBURST | Notas |
|----|---------|-------------------|-------|
| 1 | Orion Platform 2019.4 | ✅ Sí | Primera versión comprometida |
| 2 | Orion Platform 2019.4 HF1 | ✅ Sí | Hotfix comprometido |
| 3 | Orion Platform 2019.4 HF2 | ✅ Sí | Hotfix comprometido |
| 4 | Orion Platform 2019.4 HF3 | ✅ Sí | Compilado ~20/Feb/2020 (fecha clave del ataque) |
| 5 | Orion Platform 2019.4 HF5 | ❌ No | Parche limpio (26/Mar/2020) |
| 6 | Orion Platform 2020.2 | ✅ Sí | Segunda familia de versiones comprometidas |
| 7 | Orion Platform 2020.2 HF1 | ✅ Sí | Hotfix comprometido |
| 8 | Orion Platform 2020.2.1 | ❌ No | Parche de remediación post-descubrimiento |

---

## 3. Tabla: `instalaciones` (100 registros)

Registra las instalaciones de versiones del software en organizaciones cliente. Actúa como tabla puente entre `clientes` y `versiones_software`.

| Columna | Tipo | Descripción | Valores Posibles | Ejemplo |
|---------|------|-------------|------------------|---------|
| `instalacion_id` | int | Identificador único de la instalación | 1-100 | `1` |
| `cliente_id` | int (FK) | Referencia al cliente que realizó la instalación | 1-50 (debe existir en `clientes`) | `15` |
| `version_id` | int (FK) | Referencia a la versión instalada | 1-8 (debe existir en `versiones_software`) | `6` |
| `fecha_instalacion` | date | Fecha en que se instaló la versión | 2019-11-01 a 2021-03-31 | `"2020-07-05"` |
| `nivel_datos_sensibles` | str | Nivel de sensibilidad de los datos manejados por la instalación | `Bajo`, `Medio`, `Alto`, `Crítico` | `"Alto"` |

**Clave primaria**: `instalacion_id`
**Claves foráneas**:
- `cliente_id` → `clientes.cliente_id`
- `version_id` → `versiones_software.version_id`

**Restricciones**:
- `fecha_instalacion` >= `versiones_software.fecha_release` (de la versión correspondiente)
- `fecha_instalacion` <= 2021-03-31

---

## 4. Tabla: `eventos_seguridad` (200 registros)

Registra eventos de seguridad observados en las instalaciones. Generada por el Rol 2.

| Columna | Tipo | Descripción | Valores Posibles | Ejemplo |
|---------|------|-------------|------------------|---------|
| `evento_id` | int | Identificador único del evento | 1-200 | `1` |
| `instalacion_id` | int (FK) | Referencia a la instalación donde ocurrió el evento | 1-100 (debe existir en `instalaciones`) | `42` |
| `timestamp` | datetime | Fecha y hora del evento | 2019-11 a 2021-03 | `"2020-08-15 14:23:45"` |
| `tipo_evento` | str | Tipo de actividad registrada | `acceso_normal`, `descarga_datos`, `escalamiento_privilegios`, `conexion_c2`, `exfiltracion`, `reconocimiento`, `movimiento_lateral`, `persistencia`, `alerta_ids`, `modificacion_logs` | `"conexion_c2"` |
| `severidad` | str | Nivel de severidad del evento | `Baja`, `Media`, `Alta`, `Crítica` | `"Crítica"` |
| `es_anomalo` | bool | Indica si el evento fue clasificado como anómalo | `True`, `False` | `True` |

**Clave primaria**: `evento_id`
**Clave foránea**: `instalacion_id` → `instalaciones.instalacion_id`

**Notas**:
- ~80% de eventos ocurren en instalaciones con versiones SUNBURST
- ~5-7% de eventos son marcados como anómalos
- Eventos anómalos solo ocurren en instalaciones con versiones SUNBURST
- Los eventos anómalos tienden a ser de tipos más severos (conexion_c2, exfiltracion)

---

## 5. Tabla: `reporte_calidad` (resumen de métricas)

Contiene los resultados del análisis de calidad de datos según DAMA DMBOK. Generada por el Rol 2.

| Columna | Tipo | Descripción | Valores Posibles | Ejemplo |
|---------|------|-------------|------------------|---------|
| `tabla` | str | Nombre de la tabla evaluada | `clientes`, `versiones_software`, `instalaciones` | `"clientes"` |
| `columna` | str | Nombre de la columna evaluada | Nombre de columna o descripción de relación | `"cliente_id"` |
| `metrica` | str | Métrica DAMA aplicada | `Completitud`, `Exactitud`, `Consistencia` | `"Completitud"` |
| `valor_actual` | float | Valor obtenido de la métrica (porcentaje) | 0.0 - 100.0 | `100.0` |
| `umbral` | float | Umbral mínimo aceptable | 90.0, 95.0, 100.0 | `95.0` |
| `estado` | str | Resultado de la evaluación | `APROBADO`, `FALLIDO` | `"APROBADO"` |

---

## Diagrama de Relaciones

```
clientes (1) ──────────┐
                        │ FK: cliente_id
                        ▼
                   instalaciones (N:M)
                        ▲
                        │ FK: version_id
versiones_software (1) ─┘
                        
                        │ FK: instalacion_id
                        ▼
                   eventos_seguridad (1:N)
```

---

## Notas Técnicas

- **Reproducibilidad**: Todos los datos se generan con `np.random.seed(42)` y `Faker.seed(42)`
- **Encoding**: Todos los CSV usan codificación UTF-8
- **Formato de fechas**: ISO 8601 (`YYYY-MM-DD` para fechas, `YYYY-MM-DD HH:MM:SS` para timestamps)
- **Separador CSV**: Coma (`,`)
- **Sin índice**: Los CSV se exportan sin índice de pandas (`index=False`)
