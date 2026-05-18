# Decisiones de Modelado - Rol 1

## Proyecto: Análisis de Gestión de Datos del Caso SUNBURST de SolarWinds
### Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

---

## 1. Justificación del Modelo Entidad-Relación

### ¿Por qué 3 entidades?

Se diseñó un modelo con **3 entidades principales** (Clientes, Versiones_Software, Instalaciones) porque captura la estructura fundamental del escenario SUNBURST de manera clara y suficiente:

1. **Clientes**: Representa las organizaciones que utilizaban SolarWinds Orion. Es esencial modelar quién fue afectado, su tipo, sector y nivel de criticidad.

2. **Versiones_Software**: Captura las distintas versiones de la Plataforma Orion. La distinción entre versiones comprometidas y limpias es el eje central del análisis del caso.

3. **Instalaciones**: Es la tabla puente que conecta clientes con versiones. Permite responder la pregunta central: *¿qué organizaciones instalaron versiones comprometidas?*

### ¿Por qué no más entidades?

Se decidió no incluir entidades adicionales en el Rol 1 (como eventos o métricas) porque:
- El Rol 1 se enfoca en el **modelado base** del escenario
- Los eventos de seguridad son responsabilidad del Rol 2
- Un modelo con 3 entidades es suficientemente complejo para demostrar relaciones y cardinalidades sin ser abrumador

---

## 2. Selección de Atributos

### Tabla Clientes (6 atributos)

| Atributo | Justificación |
|----------|--------------|
| `cliente_id` | Identificador único necesario como clave primaria |
| `nombre_organizacion` | Identifica la organización (generado con Faker para datos realistas) |
| `tipo_org` | Distingue entre gobierno, empresas privadas, etc. Clave porque el caso afectó especialmente a agencias gubernamentales |
| `pais` | Principalmente EE.UU. (70%) ya que SolarWinds es una empresa americana y sus clientes principales son norteamericanos |
| `sector` | Permite analizar qué industrias fueron más afectadas (Tecnología, Defensa, Energía fueron las del caso real) |
| `criticidad` | Correlacionada con tipo_org: organizaciones gubernamentales y de defensa tienen criticidad más alta |

### Tabla Versiones_Software (5 atributos)

| Atributo | Justificación |
|----------|--------------|
| `version_id` | Clave primaria |
| `nombre_version` | Nombres reales de las versiones de Orion Platform del caso |
| `fecha_release` | Fechas basadas en el timeline real del caso (Anexo 1 del caso Harvard) |
| `contiene_sunburst` | **Atributo clave**: booleano que distingue versiones comprometidas de parches limpios |
| `fecha_compilacion` | Relevante porque la fecha del 20/Feb/2020 es cuando se compiló SUNBURST |

### Tabla Instalaciones (5 atributos)

| Atributo | Justificación |
|----------|--------------|
| `instalacion_id` | Clave primaria |
| `cliente_id` | FK a Clientes - permite rastrear qué organización instaló |
| `version_id` | FK a Versiones - permite saber qué versión se instaló |
| `fecha_instalacion` | Temporal - siempre posterior al release de la versión |
| `nivel_datos_sensibles` | Correlacionado con la criticidad del cliente - fundamental para evaluar impacto |

---

## 3. Cardinalidades y Relaciones

### Clientes → Instalaciones (1:N)
- Un cliente puede tener **múltiples instalaciones** (diferentes versiones en diferentes momentos)
- Cada instalación pertenece a **un solo cliente**
- **Justificación**: En el caso real, las organizaciones podían tener múltiples servidores con Orion instalado, e incluso actualizar de una versión a otra

### Versiones → Instalaciones (1:N)
- Una versión puede estar en **múltiples instalaciones** (muchas organizaciones descargan la misma versión)
- Cada instalación corresponde a **una sola versión**
- **Justificación**: Refleja el modelo de distribución de software donde una versión se distribuye a miles de clientes

### Efecto N:M
- La tabla Instalaciones actúa como **tabla puente** que resuelve la relación muchos-a-muchos entre Clientes y Versiones
- Permite consultas como: *¿Cuántos clientes de criticidad Alta instalaron versiones con SUNBURST?*

---

## 4. Decisiones sobre Datos Sintéticos

### Volúmenes
- **50 clientes**: Suficiente variedad para análisis estadístico, representando una muestra del universo de 18,000
- **8 versiones**: Todas las versiones relevantes mencionadas en el caso
- **100 instalaciones**: 2x el número de clientes, permite que algunos clientes tengan múltiples instalaciones

### Distribuciones
- **Países**: 70% EE.UU. (refleja la base de clientes real de SolarWinds)
- **Criticidad gubernamental**: 60% Alta (las agencias gubernamentales manejan información sensible)
- **Versiones**: Mayor probabilidad para Orion 2020.2 (25%), la versión más distribuida
- **Datos sensibles**: Correlacionados con criticidad del cliente (Alta → Crítico/Alto)

### Reproducibilidad
- **Semilla fija**: `np.random.seed(42)` y `Faker.seed(42)` garantizan que los mismos datos se generan cada vez
- **Validación temporal**: Cada fecha de instalación es posterior a la fecha de release de la versión correspondiente
- **Integridad referencial**: Todos los FK apuntan a registros existentes

---

## 5. Coherencia con el Caso Real

| Aspecto | Caso Real | Datos Sintéticos |
|---------|-----------|------------------|
| Versiones con SUNBURST | 2019.4 hasta HF4, 2020.2, 2020.2 HF1 | 6 de 8 versiones (75%) |
| Parches limpios | 2019.4 HF5, 2020.2.1 | 2 de 8 versiones (25%) |
| Clientes afectados | ~18,000 descargas | 78% de instalaciones con versiones SUNBURST |
| Tipo de clientes | Gobierno, Tech, Defensa | Mix similar con énfasis en gobierno |
| Período temporal | Ene 2019 - May 2021 | Oct 2019 - Mar 2021 (período de instalaciones) |
