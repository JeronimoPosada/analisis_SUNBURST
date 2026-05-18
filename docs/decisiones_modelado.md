# Decisiones de Modelado - Rol 1

## Proyecto: Analisis de Gestion de Datos del Caso SUNBURST de SolarWinds
### Universidad de San Buenaventura | Gestion de Datos | 3er Semestre

---

## 1. Justificacion del Modelo Entidad-Relacion

### Estructura de 3+1 Entidades

Se diseno un modelo con **4 entidades** (3 base + 1 del Rol 2):

| Entidad | Responsable | Registros | Justificacion |
|---------|-------------|-----------|---------------|
| **Clientes** | Rol 1 | 50+1 dup | Organizaciones que usaban Orion |
| **Versiones_Software** | Rol 1 | 8 | Versiones de Orion (SUNBURST vs limpias) |
| **Instalaciones** | Rol 1 | 100 | Tabla puente cliente-version |
| **Eventos_Seguridad** | Rol 2 | 200 | Actividad de seguridad en instalaciones |

### Diagrama ER

El diagrama se genera como `visualizations/ER.png` usando matplotlib. Muestra las 4 entidades con sus claves primarias, foraneas y atributos.

### Relaciones

- **Clientes -> Instalaciones (1:N)**: Un cliente puede tener multiples instalaciones
- **Versiones -> Instalaciones (1:N)**: Una version puede estar en multiples organizaciones
- **Instalaciones -> Eventos (1:N)**: Una instalacion genera multiples eventos de seguridad

---

## 2. Seleccion de Atributos

### Tabla Clientes

| Atributo | Tipo | Justificacion |
|----------|------|---------------|
| cliente_id | INT (PK) | Identificador unico |
| nombre_organizacion | VARCHAR | Generado con Faker para datos realistas |
| tipo_org | VARCHAR | Gobierno, Empresa, etc. (gobierno = target principal del caso) |
| pais | VARCHAR | 70% EE.UU. (refleja la base real de SolarWinds) |
| sector | VARCHAR | Tecnologia, Defensa, Energia (sectores del caso real) |
| criticidad | VARCHAR | Correlacionada con tipo_org: gobierno = Alta |

### Tabla Versiones_Software

| Atributo | Tipo | Justificacion |
|----------|------|---------------|
| version_id | INT (PK) | Identificador unico |
| nombre_version | VARCHAR | Nombres reales del caso (Orion Platform 2019.4, etc.) |
| fecha_release | DATE | Basado en timeline real |
| contiene_sunburst | BOOLEAN | Clave para distinguir versiones comprometidas |
| fecha_compilacion | DATE | 20/Feb/2020 es la fecha clave del ataque |

### Tabla Instalaciones

| Atributo | Tipo | Justificacion |
|----------|------|---------------|
| instalacion_id | INT (PK) | Identificador unico |
| cliente_id | INT (FK) | Vinculo al cliente (con anomalias intencionales) |
| version_id | INT (FK) | Vinculo a la version instalada |
| fecha_instalacion | DATE | Posterior al release (con excepciones como anomalia) |
| nivel_datos_sensibles | VARCHAR | Correlacionado con criticidad del cliente |

---

## 3. Anomalias Intencionales

### Por que inyectar anomalias?

En un entorno real, los datos **nunca** son perfectos. Un analisis de calidad que reporta 100% en todas las metricas no es creible ni util. Las anomalias se inyectaron para:

1. **Simular la realidad** de datos migrados, importados o capturados manualmente
2. **Probar la capacidad del Rol 2** de detectar problemas genuinos
3. **Generar metricas DAMA que realmente fallen** y permitan un analisis critico
4. **Demostrar el valor del framework DAMA DMBOK** en la practica

### Anomalias inyectadas por tabla

#### Clientes (5 anomalias)
| Tipo | Detalle | Simulando |
|------|---------|-----------|
| 3 nulos en nombre | Filas 7, 23, 41 | Formularios de registro incompletos |
| 2 paises vacios | Filas 15, 33 (string vacio, no NULL) | Campo obligatorio llenado con espacio |
| 1 tipo_org invalido | 'Desconocido' en fila 28 | Valor por defecto mal configurado |
| 1 criticidad nula | Fila 45 | Campo no evaluado |
| 1 ID duplicado | cliente_id=12 aparece 2 veces | Error de migracion de datos |

#### Versiones (1 anomalia)
| Tipo | Detalle | Simulando |
|------|---------|-----------|
| 1 fecha_release nula | Version HF2 (ID=3) | Dato faltante en el registro historico |

#### Instalaciones (6 anomalias)
| Tipo | Detalle | Simulando |
|------|---------|-----------|
| 3 fechas inconsistentes | Antes del release (filas 5, 20, 56) | Error humano en la captura de fechas |
| 2 FK cliente invalidas | IDs 999, 888 | Datos de clientes eliminados sin limpiar |
| 1 FK version invalida | ID 99 | Referencia a version deprecada |
| 2 nivel_sensibles nulos | Filas 9, 73 | Clasificacion pendiente |
| 1 nivel_sensibles invalido | 'Desconocido' (fila 51) | Valor por defecto |
| 1 fecha fuera de rango | 2023-11-15 (fila 89) | Error de tipeo en el ano |

---

## 4. Coherencia con el Caso Real

| Aspecto | Caso Real | Datos Sinteticos |
|---------|-----------|------------------|
| Versiones con SUNBURST | 6 versiones | 6 de 8 (75%) |
| Parches limpios | 2 versiones | 2 de 8 (25%) |
| Descargas afectadas | ~18,000 | ~77% de instalaciones SUNBURST |
| Comprometidos reales | <100 | ~11 instalaciones (~14%) |
| Tipo de clientes | Gobierno, Tech, Defensa | Mix similar con enfasis gobierno |
| Periodo temporal | Ene 2019 - May 2021 | Oct 2019 - Mar 2021 |
| **Calidad de datos** | **Imperfecta (caso real)** | **Imperfecta (anomalias intencionales)** |

---

## 5. Reproducibilidad

- **Semilla fija**: `np.random.seed(42)` y `Faker.seed(42)`
- **Anomalias deterministas**: Se inyectan en posiciones fijas (mismos datos cada ejecucion)
- **Diagrama ER**: Generado programaticamente, no requiere herramienta externa
