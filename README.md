# 🛡️ Análisis de Gestión de Datos - Caso SUNBURST (SolarWinds)

## Descripción

Proyecto de análisis del incidente cibernético **SUNBURST** que afectó a SolarWinds, abordado desde la perspectiva de **gestión de datos** aplicando el marco **DAMA DMBOK** y el **ciclo de vida de datos**.

Se generan datasets sintéticos con Python que simulan el escenario del ataque y se aplican métricas de calidad de datos para analizar el impacto.

### Contexto del Caso
- **SUNBURST** fue un ciberataque sofisticado que comprometió la Plataforma Orion de SolarWinds
- ~18,000 organizaciones descargaron versiones afectadas
- Menos de 100 fueron realmente comprometidas
- Afectó a agencias gubernamentales de EE.UU. (Dept. Energía, Justicia, Tesoro, CISA, Pentágono)

---

## Estructura del Proyecto

```
Actividad_SUNBURST/
├── 📂 data/                         # Archivos CSV generados
│   ├── clientes.csv                 # 50 organizaciones cliente
│   ├── versiones_software.csv       # 8 versiones de Orion Platform
│   ├── instalaciones.csv            # 100 instalaciones
│   ├── eventos_seguridad.csv        # 200 eventos de seguridad
│   └── reporte_calidad.csv          # Métricas DAMA DMBOK
│
├── 📂 notebooks/                    # Jupyter Notebooks (explicativos)
│   ├── rol1_modelado.ipynb          # Modelado ER y generación de datos
│   ├── rol2_calidad.ipynb           # Análisis de calidad y anomalías
│   └── rol3_integracion.ipynb       # Integración (pendiente)
│
├── 📂 scripts/                      # Scripts Python (ejecutables)
│   ├── rol1_generacion_datos.py     # Funciones de generación de datos
│   ├── rol2_calidad_datos.py        # Funciones de validación y análisis
│   └── rol3_integracion.py          # Integración (pendiente)
│
├── 📂 visualizations/               # Gráficos generados
│   ├── anomalias.png                # Distribución de anomalías
│   ├── severidad_eventos.png        # Severidad de eventos
│   ├── clientes_afectados.png       # Análisis de clientes
│   ├── calidad_datos.png            # Heatmap métricas DAMA
│   └── grafico_cascada.png          # Cascada 18,000 → <100
│
├── 📂 docs/                         # Documentación
│   ├── Actividad_Analisis_SUNBURST_Gestion_Datos.pdf  # Actividad
│   ├── Caso SolarWins.pdf           # Caso de estudio Harvard
│   ├── decisiones_modelado.md       # Decisiones del Rol 1
│   ├── analisis_calidad.md          # Análisis del Rol 2
│   └── diccionario_datos.md         # Diccionario de datos completo
│
├── README.md                        # Este archivo
└── requirements.txt                 # Dependencias Python
```

---

## Roles y Responsabilidades

| Rol | Responsabilidad | Entregables |
|-----|----------------|-------------|
| **Rol 1**: Diseñador de Datos | Modelado ER y generación de datos sintéticos | `clientes.csv`, `versiones_software.csv`, `instalaciones.csv` |
| **Rol 2**: Analista de Calidad | Validación DAMA DMBOK y detección de anomalías | `eventos_seguridad.csv`, `reporte_calidad.csv`, 5 gráficos |
Rol 3: Integrador | Consolidación, integración y ciclo de vida | `eventos_ciclo_vida.csv`, `resumen_impacto.csv`, `dashboard`|

---

## Tecnologías Utilizadas

- **Python 3.8+**
- **pandas**: Manipulación y análisis de datos
- **numpy**: Cálculos numéricos y generación aleatoria
- **faker**: Generación de datos ficticios realistas
- **matplotlib**: Visualizaciones y gráficos
- **seaborn**: Gráficos estadísticos avanzados
- **jupyter**: Notebooks interactivos

---

## Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/JeronimoPosada/analisis_SUNBURST.git
cd Actividad_SUNBURST
```

### 2. Crear entorno virtual e instalar dependencias
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### 3. Ejecutar scripts

```bash
# Rol 1: Generar datos base
python scripts/rol1_generacion_datos.py

# Rol 2: Análisis de calidad
python scripts/rol2_calidad_datos.py
```
# Rol 3: integración de codigo
rol3_integracion.ipynb          # Integración y ciclo de vida de datos
rol3_integracion.py             # Consolidación y análisis DAMA DMBOK

### 4. Explorar notebooks
```bash
jupyter notebook notebooks/
```

---

## Datos Generados

| Dataset | Registros | Generado por |
|---------|-----------|-------------|
| `clientes.csv` | 50 | Rol 1 |
| `versiones_software.csv` | 8 | Rol 1 |
| `instalaciones.csv` | 100 | Rol 1 |
| `eventos_seguridad.csv` | 200 | Rol 2 |
| `reporte_calidad.csv` | 35 métricas | Rol 2 |

> **Nota**: Los datos son sintéticos (ficticios) pero coherentes con el contexto del caso SUNBURST.
> Se usa `np.random.seed(42)` para reproducibilidad.

---

## Curso
**Gestión de Datos** — Universidad de San Buenaventura — 3er Semestre
