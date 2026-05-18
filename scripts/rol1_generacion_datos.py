"""
=============================================================================
ROL 1: Diseñador de Datos - Generación de Datos Sintéticos
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

Este script genera datasets sintéticos que simulan el escenario del ataque
SUNBURST a SolarWinds. Se generan 3 DataFrames principales:
  - clientes (50 registros): organizaciones que usaban la Plataforma Orion
  - versiones_software (8 registros): versiones de la Plataforma Orion
  - instalaciones (100 registros): instalaciones de software en clientes

NOTA: Los datos contienen anomalías intencionales para que el Rol 2
pueda detectarlas y analizarlas de forma realista.

Uso:
    python rol1_generacion_datos.py
=============================================================================
"""

import pandas as pd
import numpy as np
from faker import Faker
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
from datetime import datetime, timedelta

# Configuración de reproducibilidad
np.random.seed(42)
fake = Faker('es_ES')  # Faker en español
Faker.seed(42)

# ===========================================================================
# CONSTANTES Y DATOS BASE DEL CASO SUNBURST
# ===========================================================================

TIPOS_ORGANIZACION = [
    'Gobierno Federal', 'Gobierno Estatal', 'Empresa Privada',
    'Institución Educativa', 'Organización de Salud', 'ONG'
]

SECTORES = [
    'Tecnología', 'Defensa', 'Energía', 'Finanzas',
    'Telecomunicaciones', 'Salud', 'Gobierno', 'Educación'
]

CRITICIDADES = ['Alta', 'Media', 'Baja']
NIVELES_DATOS_SENSIBLES = ['Bajo', 'Medio', 'Alto', 'Crítico']

PAISES = [
    'Estados Unidos', 'Estados Unidos', 'Estados Unidos', 'Estados Unidos',
    'Estados Unidos', 'Estados Unidos', 'Estados Unidos',
    'Reino Unido', 'Canadá', 'Alemania', 'Israel',
    'Australia', 'Francia', 'Japón'
]


def generar_clientes(n=50):
    """
    Genera un DataFrame de clientes con anomalías intencionales:
    - 3 registros con nombre_organizacion nulo
    - 2 registros con pais vacío ("")
    - 1 registro con tipo_org inválido ("Desconocido")
    - 1 registro con criticidad nula
    - 1 cliente_id duplicado (ID 12 aparece 2 veces → 51 filas reales)
    """
    print(f"[ROL1] Generando {n} clientes (con anomalías intencionales)...")

    clientes = []
    for i in range(1, n + 1):
        tipo_org = np.random.choice(TIPOS_ORGANIZACION, p=[0.15, 0.10, 0.40, 0.10, 0.15, 0.10])

        if 'Gobierno' in tipo_org:
            nombre = f"{np.random.choice(['Departamento de', 'Agencia de', 'Ministerio de'])} {fake.word().capitalize()} {fake.word().capitalize()}"
            criticidad = np.random.choice(CRITICIDADES, p=[0.6, 0.3, 0.1])
            sector = np.random.choice(['Gobierno', 'Defensa', 'Energía'])
        elif tipo_org == 'Institución Educativa':
            nombre = f"Universidad {fake.city()}"
            criticidad = np.random.choice(CRITICIDADES, p=[0.2, 0.5, 0.3])
            sector = np.random.choice(SECTORES)
        elif tipo_org == 'Organización de Salud':
            nombre = f"Hospital {fake.last_name()} {fake.city()}"
            criticidad = np.random.choice(CRITICIDADES, p=[0.5, 0.35, 0.15])
            sector = 'Salud'
        else:
            nombre = f"{fake.company()}"
            criticidad = np.random.choice(CRITICIDADES, p=[0.2, 0.5, 0.3])
            sector = np.random.choice(SECTORES)

        clientes.append({
            'cliente_id': i,
            'nombre_organizacion': nombre,
            'tipo_org': tipo_org,
            'pais': np.random.choice(PAISES),
            'sector': sector,
            'criticidad': criticidad
        })

    df = pd.DataFrame(clientes)

    # =====================================================================
    # INYECCIÓN DE ANOMALÍAS INTENCIONALES
    # =====================================================================
    print("    ⚠️  Inyectando anomalías intencionales...")

    # Anomalía 1: 3 nombres de organización nulos (filas 7, 23, 41)
    df.loc[6, 'nombre_organizacion'] = None
    df.loc[22, 'nombre_organizacion'] = None
    df.loc[40, 'nombre_organizacion'] = None
    print("      → 3 nombre_organizacion = NULL (filas 7, 23, 41)")

    # Anomalía 2: 2 países vacíos (filas 15, 33)
    df.loc[14, 'pais'] = ''
    df.loc[32, 'pais'] = ''
    print("      → 2 pais = '' (filas 15, 33)")

    # Anomalía 3: 1 tipo_org inválido (fila 28)
    df.loc[27, 'tipo_org'] = 'Desconocido'
    print("      → 1 tipo_org = 'Desconocido' (fila 28)")

    # Anomalía 4: 1 criticidad nula (fila 45)
    df.loc[44, 'criticidad'] = None
    print("      → 1 criticidad = NULL (fila 45)")

    # Anomalía 5: 1 cliente_id duplicado (duplicar fila 12 con datos diferentes)
    fila_dup = {
        'cliente_id': 12,  # ID duplicado
        'nombre_organizacion': 'Entidad Duplicada S.A.',
        'tipo_org': 'Empresa Privada',
        'pais': 'Estados Unidos',
        'sector': 'Tecnología',
        'criticidad': 'Media'
    }
    df = pd.concat([df, pd.DataFrame([fila_dup])], ignore_index=True)
    print("      → 1 cliente_id duplicado (ID=12 aparece 2 veces)")

    print(f"    ✓ {len(df)} filas generadas (50 + 1 duplicado)")
    return df


def generar_versiones():
    """
    Genera las versiones de la Plataforma Orion con 1 anomalía:
    - 1 fecha_release nula (versión HF2)
    """
    print("[ROL1] Generando versiones de software (con anomalías)...")

    versiones = [
        {'version_id': 1, 'nombre_version': 'Orion Platform 2019.4',
         'fecha_release': datetime(2019, 10, 22), 'contiene_sunburst': True,
         'fecha_compilacion': datetime(2019, 10, 10)},
        {'version_id': 2, 'nombre_version': 'Orion Platform 2019.4 HF1',
         'fecha_release': datetime(2019, 12, 17), 'contiene_sunburst': True,
         'fecha_compilacion': datetime(2019, 12, 5)},
        {'version_id': 3, 'nombre_version': 'Orion Platform 2019.4 HF2',
         'fecha_release': None,  # ANOMALÍA: fecha_release nula
         'contiene_sunburst': True,
         'fecha_compilacion': datetime(2020, 1, 10)},
        {'version_id': 4, 'nombre_version': 'Orion Platform 2019.4 HF3',
         'fecha_release': datetime(2020, 3, 5), 'contiene_sunburst': True,
         'fecha_compilacion': datetime(2020, 2, 20)},
        {'version_id': 5, 'nombre_version': 'Orion Platform 2019.4 HF5',
         'fecha_release': datetime(2020, 3, 26), 'contiene_sunburst': False,
         'fecha_compilacion': datetime(2020, 3, 15)},
        {'version_id': 6, 'nombre_version': 'Orion Platform 2020.2',
         'fecha_release': datetime(2020, 6, 19), 'contiene_sunburst': True,
         'fecha_compilacion': datetime(2020, 6, 4)},
        {'version_id': 7, 'nombre_version': 'Orion Platform 2020.2 HF1',
         'fecha_release': datetime(2020, 9, 14), 'contiene_sunburst': True,
         'fecha_compilacion': datetime(2020, 9, 1)},
        {'version_id': 8, 'nombre_version': 'Orion Platform 2020.2.1',
         'fecha_release': datetime(2020, 12, 15), 'contiene_sunburst': False,
         'fecha_compilacion': datetime(2020, 12, 14)},
    ]

    df = pd.DataFrame(versiones)
    print(f"    ⚠️  1 fecha_release = NULL (versión HF2, ID=3)")
    print(f"    ✓ {len(df)} versiones generadas ({df['contiene_sunburst'].sum()} con SUNBURST)")
    return df


def generar_instalaciones(clientes_df, versiones_df, n=100):
    """
    Genera instalaciones con anomalías intencionales:
    - 3 fechas de instalación ANTERIORES al release (inconsistencia temporal)
    - 2 cliente_id que NO existen en clientes (FK huérfanas: 999, 888)
    - 1 version_id que NO existe en versiones (FK huérfana: 99)
    - 2 nivel_datos_sensibles nulos
    - 1 nivel_datos_sensibles inválido ("Desconocido")
    - 1 fecha fuera de rango (2023)
    """
    print(f"[ROL1] Generando {n} instalaciones (con anomalías)...")

    clientes_ids = clientes_df['cliente_id'].unique().tolist()
    versiones_ids = versiones_df['version_id'].tolist()
    version_probs = [0.15, 0.10, 0.08, 0.07, 0.10, 0.25, 0.15, 0.10]

    # Versiones con fecha release válida para calcular fechas de instalación
    versiones_con_fecha = versiones_df.dropna(subset=['fecha_release'])

    instalaciones = []
    for i in range(1, n + 1):
        version_id = np.random.choice(versiones_ids, p=version_probs)
        cliente_id = np.random.choice(clientes_ids)

        # Obtener fecha release (manejar el nulo)
        version_row = versiones_df[versiones_df['version_id'] == version_id].iloc[0]
        fecha_release = version_row['fecha_release']

        if pd.isna(fecha_release):
            # Si no hay fecha release, usar una fecha por defecto
            fecha_release = datetime(2020, 1, 23)

        dias_despues = np.random.randint(1, 91)
        fecha_instalacion = pd.to_datetime(fecha_release) + timedelta(days=int(dias_despues))

        fecha_max = datetime(2021, 3, 31)
        if fecha_instalacion > fecha_max:
            fecha_instalacion = fecha_max - timedelta(days=np.random.randint(1, 30))

        criticidad_cliente = clientes_df[clientes_df['cliente_id'] == cliente_id]['criticidad'].iloc[0]
        if pd.isna(criticidad_cliente):
            criticidad_cliente = 'Media'

        if criticidad_cliente == 'Alta':
            nivel = np.random.choice(NIVELES_DATOS_SENSIBLES, p=[0.05, 0.15, 0.40, 0.40])
        elif criticidad_cliente == 'Media':
            nivel = np.random.choice(NIVELES_DATOS_SENSIBLES, p=[0.15, 0.40, 0.30, 0.15])
        else:
            nivel = np.random.choice(NIVELES_DATOS_SENSIBLES, p=[0.40, 0.35, 0.20, 0.05])

        instalaciones.append({
            'instalacion_id': i,
            'cliente_id': cliente_id,
            'version_id': version_id,
            'fecha_instalacion': fecha_instalacion.strftime('%Y-%m-%d'),
            'nivel_datos_sensibles': nivel
        })

    df = pd.DataFrame(instalaciones)

    # =====================================================================
    # INYECCIÓN DE ANOMALÍAS INTENCIONALES
    # =====================================================================
    print("    ⚠️  Inyectando anomalías intencionales...")

    # Anomalía 1: 3 fechas ANTERIORES al release (inconsistencia temporal)
    df.loc[4, 'fecha_instalacion'] = '2019-08-15'   # Antes del primer release (Oct 2019)
    df.loc[19, 'fecha_instalacion'] = '2019-06-01'   # Imposible
    df.loc[55, 'fecha_instalacion'] = '2019-09-20'   # Antes del primer release
    print("      → 3 fecha_instalacion antes del release (filas 5, 20, 56)")

    # Anomalía 2: 2 cliente_id que no existen (FK huérfanas)
    df.loc[10, 'cliente_id'] = 999   # No existe
    df.loc[67, 'cliente_id'] = 888   # No existe
    print("      → 2 cliente_id inexistentes: 999, 888 (filas 11, 68)")

    # Anomalía 3: 1 version_id que no existe (FK huérfana)
    df.loc[35, 'version_id'] = 99    # No existe
    print("      → 1 version_id inexistente: 99 (fila 36)")

    # Anomalía 4: 2 nivel_datos_sensibles nulos
    df.loc[8, 'nivel_datos_sensibles'] = None
    df.loc[72, 'nivel_datos_sensibles'] = None
    print("      → 2 nivel_datos_sensibles = NULL (filas 9, 73)")

    # Anomalía 5: 1 nivel_datos_sensibles inválido
    df.loc[50, 'nivel_datos_sensibles'] = 'Desconocido'
    print("      → 1 nivel_datos_sensibles = 'Desconocido' (fila 51)")

    # Anomalía 6: 1 fecha completamente fuera de rango
    df.loc[88, 'fecha_instalacion'] = '2023-11-15'   # Fuera del período del caso
    print("      → 1 fecha_instalacion = 2023-11-15 (fuera de rango, fila 89)")

    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    n_sunburst = df[df['version_id'].isin(versiones_sunburst)].shape[0]
    print(f"    ✓ {len(df)} instalaciones generadas ({n_sunburst} con versiones SUNBURST)")

    return df


def generar_diagrama_er(ruta='../visualizations/'):
    """
    Genera un diagrama Entidad-Relación profesional como PNG usando matplotlib.
    El diagrama muestra las 3 entidades principales y sus relaciones.
    """
    os.makedirs(ruta, exist_ok=True)
    print("\n[ROL1] Generando diagrama ER...")

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Colores profesionales
    COLOR_HEADER = '#1a237e'    # Azul oscuro
    COLOR_PK = '#e8eaf6'       # Azul claro
    COLOR_FK = '#fff3e0'       # Naranja claro
    COLOR_ATTR = '#f5f5f5'     # Gris claro
    COLOR_REL = '#c62828'      # Rojo para relaciones
    COLOR_BORDER = '#37474f'   # Gris oscuro

    def draw_entity(ax, x, y, width, height, title, attributes, pk_count=1, fk_indices=None):
        """Dibuja una entidad del diagrama ER con estilo profesional."""
        if fk_indices is None:
            fk_indices = []

        # Marco principal
        rect = mpatches.FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.05",
            facecolor='white', edgecolor=COLOR_BORDER, linewidth=2
        )
        ax.add_patch(rect)

        # Header con nombre de entidad
        header_h = 0.55
        header = mpatches.FancyBboxPatch(
            (x, y + height - header_h), width, header_h,
            boxstyle="round,pad=0.05",
            facecolor=COLOR_HEADER, edgecolor=COLOR_BORDER, linewidth=2
        )
        ax.add_patch(header)
        ax.text(x + width/2, y + height - header_h/2, title,
                ha='center', va='center', fontsize=13, fontweight='bold',
                color='white', fontfamily='monospace')

        # Atributos
        line_h = 0.38
        for i, attr in enumerate(attributes):
            attr_y = y + height - header_h - (i + 1) * line_h

            # Color de fondo según tipo
            if i < pk_count:
                bg_color = COLOR_PK
                prefix = '[PK]  '
            elif i in fk_indices:
                bg_color = COLOR_FK
                prefix = '[FK]  '
            else:
                bg_color = COLOR_ATTR
                prefix = '      '

            attr_rect = plt.Rectangle(
                (x + 0.05, attr_y), width - 0.1, line_h - 0.02,
                facecolor=bg_color, edgecolor='#e0e0e0', linewidth=0.5
            )
            ax.add_patch(attr_rect)

            ax.text(x + 0.2, attr_y + line_h/2, f"{prefix}{attr}",
                    ha='left', va='center', fontsize=9.5, fontfamily='monospace',
                    color='#333333')

    # ===== ENTIDAD: CLIENTES =====
    clientes_attrs = [
        'cliente_id          INT',
        'nombre_organizacion VARCHAR',
        'tipo_org            VARCHAR',
        'pais                VARCHAR',
        'sector              VARCHAR',
        'criticidad          VARCHAR',
    ]
    draw_entity(ax, 0.5, 5.5, 5.0, 3.4, 'CLIENTES', clientes_attrs,
                pk_count=1)

    # ===== ENTIDAD: VERSIONES_SOFTWARE =====
    versiones_attrs = [
        'version_id          INT',
        'nombre_version      VARCHAR',
        'fecha_release       DATE',
        'contiene_sunburst   BOOLEAN',
        'fecha_compilacion   DATE',
    ]
    draw_entity(ax, 10.5, 5.5, 5.0, 3.0, 'VERSIONES_SOFTWARE', versiones_attrs,
                pk_count=1)

    # ===== ENTIDAD: INSTALACIONES =====
    inst_attrs = [
        'instalacion_id      INT',
        'cliente_id           INT',
        'version_id           INT',
        'fecha_instalacion    DATE',
        'nivel_datos_sensibles VARCHAR',
    ]
    draw_entity(ax, 4.0, 0.8, 5.5, 3.0, 'INSTALACIONES', inst_attrs,
                pk_count=1, fk_indices=[1, 2])

    # ===== ENTIDAD: EVENTOS_SEGURIDAD (Rol 2) =====
    eventos_attrs = [
        'evento_id            INT',
        'instalacion_id       INT',
        'timestamp            DATETIME',
        'tipo_evento          VARCHAR',
        'severidad            VARCHAR',
        'es_anomalo           BOOLEAN',
    ]
    draw_entity(ax, 10.5, 0.5, 5.0, 3.4, 'EVENTOS_SEGURIDAD', eventos_attrs,
                pk_count=1, fk_indices=[1])

    # ===== RELACIONES =====
    # Clientes → Instalaciones (1:N)
    ax.annotate('',
                xy=(5.0, 2.3), xytext=(3.0, 5.5),
                arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5,
                               connectionstyle='arc3,rad=-0.2'))
    ax.text(2.8, 4.0, '1:N', fontsize=12, fontweight='bold',
            color=COLOR_REL, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    # Versiones → Instalaciones (1:N)
    ax.annotate('',
                xy=(9.0, 2.3), xytext=(12.5, 5.5),
                arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5,
                               connectionstyle='arc3,rad=0.2'))
    ax.text(12.0, 4.0, '1:N', fontsize=12, fontweight='bold',
            color=COLOR_REL, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    # Instalaciones → Eventos (1:N)
    ax.annotate('',
                xy=(10.5, 1.8), xytext=(9.5, 2.0),
                arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5))
    ax.text(10.0, 2.3, '1:N', fontsize=11, fontweight='bold',
            color=COLOR_REL, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    # Título
    ax.text(8, 9.7, 'Modelo Entidad-Relación — Caso SUNBURST',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color=COLOR_HEADER, fontfamily='sans-serif')
    ax.text(8, 9.25, 'Análisis de Gestión de Datos | SolarWinds Orion Platform',
            ha='center', va='center', fontsize=11, color='#666666', style='italic')

    # Leyenda
    legend_y = 4.5
    legend_x = 0.6
    ax.text(legend_x, legend_y, 'Leyenda:', fontsize=10, fontweight='bold', color='#333')
    for i, (color, label) in enumerate([
        (COLOR_PK, 'Clave Primaria (PK)'), (COLOR_FK, 'Clave Foránea (FK)'),
        (COLOR_ATTR, 'Atributo'), ('#ffffff', 'Línea roja = Relación')
    ]):
        rect = plt.Rectangle((legend_x, legend_y - 0.42*(i+1)), 0.3, 0.25,
                              facecolor=color, edgecolor='#999', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(legend_x + 0.45, legend_y - 0.42*(i+1) + 0.12, label,
                fontsize=8.5, va='center', color='#555')

    plt.tight_layout()
    filepath = os.path.join(ruta, 'ER.png')
    plt.savefig(filepath, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    ✓ Diagrama ER guardado → {filepath}")


def guardar_csvs(clientes_df, versiones_df, instalaciones_df, ruta='../data/'):
    """
    Guarda los DataFrames generados como archivos CSV.
    """
    os.makedirs(ruta, exist_ok=True)

    archivos = {
        'clientes.csv': clientes_df,
        'versiones_software.csv': versiones_df,
        'instalaciones.csv': instalaciones_df
    }

    print("\n[ROL1] Guardando archivos CSV...")
    for nombre, df in archivos.items():
        filepath = os.path.join(ruta, nombre)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"    ✓ {nombre} guardado ({len(df)} registros) → {filepath}")

    print("\n[ROL1] ¡Generación de datos completada exitosamente!")


# ===========================================================================
# EJECUCIÓN PRINCIPAL
# ===========================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  ROL 1: GENERACIÓN DE DATOS SINTÉTICOS - CASO SUNBURST")
    print("  (Con anomalías intencionales para análisis de calidad)")
    print("=" * 70)
    print()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    vis_dir = os.path.join(script_dir, '..', 'visualizations')

    # 1. Generar datos
    clientes = generar_clientes(n=50)
    print()
    versiones = generar_versiones()
    print()
    instalaciones = generar_instalaciones(clientes, versiones, n=100)

    # 2. Generar diagrama ER
    generar_diagrama_er(ruta=vis_dir)

    # 3. Vista previa
    print()
    print("-" * 70)
    print("VISTA PREVIA DE LOS DATOS GENERADOS")
    print("-" * 70)
    print(f"\n📋 Clientes (primeros 5):")
    print(clientes.head().to_string(index=False))
    print(f"\n📋 Versiones Software:")
    print(versiones.to_string(index=False))
    print(f"\n📋 Instalaciones (primeros 5):")
    print(instalaciones.head().to_string(index=False))

    # 4. Resumen de anomalías
    print()
    print("-" * 70)
    print("⚠️  RESUMEN DE ANOMALÍAS INYECTADAS")
    print("-" * 70)
    print("Clientes:")
    print(f"  • {clientes['nombre_organizacion'].isnull().sum()} nombres nulos")
    print(f"  • {(clientes['pais'] == '').sum()} países vacíos")
    print(f"  • {clientes[~clientes['tipo_org'].isin(TIPOS_ORGANIZACION)].shape[0]} tipo_org inválidos")
    print(f"  • {clientes['criticidad'].isnull().sum()} criticidad nula")
    print(f"  • {clientes['cliente_id'].duplicated().sum()} IDs duplicados")
    print("Versiones:")
    print(f"  • {versiones['fecha_release'].isnull().sum()} fecha_release nula")
    print("Instalaciones:")
    cli_ids_validos = set(clientes['cliente_id'].unique())
    ver_ids_validos = set(versiones['version_id'])
    print(f"  • {instalaciones[~instalaciones['cliente_id'].isin(cli_ids_validos)].shape[0]} FK cliente_id inválidos")
    print(f"  • {instalaciones[~instalaciones['version_id'].isin(ver_ids_validos)].shape[0]} FK version_id inválidos")
    print(f"  • {instalaciones['nivel_datos_sensibles'].isnull().sum()} nivel_datos_sensibles nulos")

    # 5. Guardar CSVs
    print()
    guardar_csvs(clientes, versiones, instalaciones, ruta=data_dir)
