"""
=============================================================================
ROL 1: Diseñador de Datos - Generación de Datos Sintéticos
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre
Uso: python scripts/rol1_generacion_datos.py
=============================================================================
"""

import pandas as pd
import numpy as np
from faker import Faker
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuración de reproducibilidad
np.random.seed(42)
fake = Faker('es_ES')
Faker.seed(42)

TIPOS_ORGANIZACION = ['Gobierno Federal', 'Gobierno Estatal', 'Empresa Privada', 'Institución Educativa', 'Organización de Salud', 'ONG']
SECTORES = ['Tecnología', 'Defensa', 'Energía', 'Finanzas', 'Telecomunicaciones', 'Salud', 'Gobierno', 'Educación']
CRITICIDADES = ['Alta', 'Media', 'Baja']
NIVELES_DATOS_SENSIBLES = ['Bajo', 'Medio', 'Alto', 'Crítico']
PAISES = ['Estados Unidos'] * 7 + ['Reino Unido', 'Canadá', 'Alemania', 'Israel', 'Australia', 'Francia', 'Japón']

def generar_clientes(n=50):
    print(f"[ROL1] Generando {n} clientes (con anomalías intencionales)...")
    clientes = []
    for i in range(1, n + 1):
        tipo_org = np.random.choice(TIPOS_ORGANIZACION, p=[0.15, 0.10, 0.40, 0.10, 0.15, 0.10])
        clientes.append({
            'cliente_id': i,
            'nombre_organizacion': fake.company(),
            'tipo_org': tipo_org,
            'pais': np.random.choice(PAISES),
            'sector': np.random.choice(SECTORES),
            'criticidad': np.random.choice(CRITICIDADES)
        })

    df = pd.DataFrame(clientes)
    print("    ⚠️  Inyectando anomalías intencionales...")
    df.loc[6, 'nombre_organizacion'] = None
    df.loc[22, 'nombre_organizacion'] = None
    df.loc[40, 'nombre_organizacion'] = None
    df.loc[14, 'pais'] = ''
    df.loc[32, 'pais'] = ''
    df.loc[27, 'tipo_org'] = 'Desconocido'
    df.loc[44, 'criticidad'] = None
    
    fila_dup = {'cliente_id': 12, 'nombre_organizacion': 'Entidad Duplicada S.A.', 'tipo_org': 'Empresa Privada', 'pais': 'Estados Unidos', 'sector': 'Tecnología', 'criticidad': 'Media'}
    df = pd.concat([df, pd.DataFrame([fila_dup])], ignore_index=True)
    print(f"    ✓ {len(df)} filas generadas")
    return df

def generar_versiones():
    print("[ROL1] Generando versiones de software (con anomalías)...")
    versiones = [
        {'version_id': 1, 'nombre_version': 'Orion Platform 2019.4', 'fecha_release': pd.to_datetime('2019-10-22'), 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2019-10-10')},
        {'version_id': 2, 'nombre_version': 'Orion Platform 2019.4 HF1', 'fecha_release': pd.to_datetime('2019-12-17'), 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2019-12-05')},
        {'version_id': 3, 'nombre_version': 'Orion Platform 2019.4 HF2', 'fecha_release': pd.NaT, 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2020-01-10')},
        {'version_id': 4, 'nombre_version': 'Orion Platform 2019.4 HF3', 'fecha_release': pd.to_datetime('2020-03-05'), 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2020-02-20')},
        {'version_id': 5, 'nombre_version': 'Orion Platform 2019.4 HF5', 'fecha_release': pd.to_datetime('2020-03-26'), 'contiene_sunburst': False, 'fecha_compilacion': pd.to_datetime('2020-03-15')},
        {'version_id': 6, 'nombre_version': 'Orion Platform 2020.2', 'fecha_release': pd.to_datetime('2020-06-19'), 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2020-06-04')},
        {'version_id': 7, 'nombre_version': 'Orion Platform 2020.2 HF1', 'fecha_release': pd.to_datetime('2020-09-14'), 'contiene_sunburst': True, 'fecha_compilacion': pd.to_datetime('2020-09-01')},
        {'version_id': 8, 'nombre_version': 'Orion Platform 2020.2.1', 'fecha_release': pd.to_datetime('2020-12-15'), 'contiene_sunburst': False, 'fecha_compilacion': pd.to_datetime('2020-12-14')},
    ]
    df = pd.DataFrame(versiones)
    print(f"    ✓ {len(df)} versiones generadas")
    return df

def generar_instalaciones(clientes_df, versiones_df, n=100):
    print(f"[ROL1] Generando {n} instalaciones (con anomalías)...")
    clientes_ids = clientes_df['cliente_id'].unique().tolist()
    versiones_ids = versiones_df['version_id'].tolist()
    
    instalaciones = []
    for i in range(1, n + 1):
        version_id = np.random.choice(versiones_ids)
        cliente_id = np.random.choice(clientes_ids)
        
        row = versiones_df[versiones_df['version_id'] == version_id].iloc[0]
        fecha_rel = row['fecha_release']
        if pd.isna(fecha_rel):
            fecha_rel = pd.to_datetime('2020-01-23')
            
        dias_despues = np.random.randint(1, 91)
        fecha_inst = fecha_rel + pd.Timedelta(days=dias_despues)
        
        fecha_max = pd.to_datetime('2021-03-31')
        if fecha_inst > fecha_max:
            fecha_inst = fecha_max - pd.Timedelta(days=np.random.randint(1, 30))
            
        instalaciones.append({
            'instalacion_id': i,
            'cliente_id': cliente_id,
            'version_id': version_id,
            'fecha_instalacion': fecha_inst.strftime('%Y-%m-%d'),
            'nivel_datos_sensibles': np.random.choice(NIVELES_DATOS_SENSIBLES)
        })

    df = pd.DataFrame(instalaciones)
    print("    ⚠️  Inyectando anomalías intencionales...")
    df.loc[4, 'fecha_instalacion'] = '2019-08-15'
    df.loc[19, 'fecha_instalacion'] = '2019-06-01'
    df.loc[55, 'fecha_instalacion'] = '2019-09-20'
    df.loc[10, 'cliente_id'] = 999
    df.loc[67, 'cliente_id'] = 888
    df.loc[35, 'version_id'] = 99
    df.loc[8, 'nivel_datos_sensibles'] = None
    df.loc[72, 'nivel_datos_sensibles'] = None
    df.loc[50, 'nivel_datos_sensibles'] = 'Desconocido'
    df.loc[88, 'fecha_instalacion'] = '2023-11-15'
    print(f"    ✓ {len(df)} instalaciones generadas")
    return df

def generar_diagrama_er(ruta='visualizations/'):
    print("\n[ROL1] Generando diagrama ER (Restaurado a profesional)...")
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Colores profesionales
    COLOR_HEADER = '#1a237e'
    COLOR_PK = '#e8eaf6'
    COLOR_FK = '#fff3e0'
    COLOR_ATTR = '#f5f5f5'
    COLOR_REL = '#c62828'
    COLOR_BORDER = '#37474f'

    def draw_entity(ax, x, y, width, height, title, attributes, pk_count=1, fk_indices=None):
        if fk_indices is None:
            fk_indices = []

        rect = mpatches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.05", facecolor='white', edgecolor=COLOR_BORDER, linewidth=2)
        ax.add_patch(rect)

        header_h = 0.55
        header = mpatches.FancyBboxPatch((x, y + height - header_h), width, header_h, boxstyle="round,pad=0.05", facecolor=COLOR_HEADER, edgecolor=COLOR_BORDER, linewidth=2)
        ax.add_patch(header)
        ax.text(x + width/2, y + height - header_h/2, title, ha='center', va='center', fontsize=13, fontweight='bold', color='white', fontfamily='monospace')

        line_h = 0.38
        for i, attr in enumerate(attributes):
            attr_y = y + height - header_h - (i + 1) * line_h
            if i < pk_count:
                bg_color = COLOR_PK
                prefix = '[PK]  '
            elif i in fk_indices:
                bg_color = COLOR_FK
                prefix = '[FK]  '
            else:
                bg_color = COLOR_ATTR
                prefix = '      '

            attr_rect = plt.Rectangle((x + 0.05, attr_y), width - 0.1, line_h - 0.02, facecolor=bg_color, edgecolor='#e0e0e0', linewidth=0.5)
            ax.add_patch(attr_rect)
            ax.text(x + 0.2, attr_y + line_h/2, f"{prefix}{attr}", ha='left', va='center', fontsize=9.5, fontfamily='monospace', color='#333333')

    # ===== ENTIDADES =====
    clientes_attrs = ['cliente_id          INT', 'nombre_organizacion VARCHAR', 'tipo_org            VARCHAR', 'pais                VARCHAR', 'sector              VARCHAR', 'criticidad          VARCHAR']
    draw_entity(ax, 0.5, 5.5, 5.0, 3.4, 'CLIENTES', clientes_attrs, pk_count=1)

    versiones_attrs = ['version_id          INT', 'nombre_version      VARCHAR', 'fecha_release       DATE', 'contiene_sunburst   BOOLEAN', 'fecha_compilacion   DATE']
    draw_entity(ax, 10.5, 5.5, 5.0, 3.0, 'VERSIONES_SOFTWARE', versiones_attrs, pk_count=1)

    inst_attrs = ['instalacion_id      INT', 'cliente_id           INT', 'version_id           INT', 'fecha_instalacion    DATE', 'nivel_datos_sensibles VARCHAR']
    draw_entity(ax, 4.0, 0.8, 5.5, 3.0, 'INSTALACIONES', inst_attrs, pk_count=1, fk_indices=[1, 2])

    eventos_attrs = ['evento_id            INT', 'instalacion_id       INT', 'timestamp            DATETIME', 'tipo_evento          VARCHAR', 'severidad            VARCHAR', 'es_anomalo           BOOLEAN']
    draw_entity(ax, 10.5, 0.5, 5.0, 3.4, 'EVENTOS_SEGURIDAD', eventos_attrs, pk_count=1, fk_indices=[1])

    # ===== RELACIONES =====
    ax.annotate('', xy=(5.0, 2.3), xytext=(3.0, 5.5), arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5, connectionstyle='arc3,rad=-0.2'))
    ax.text(2.8, 4.0, '1:N', fontsize=12, fontweight='bold', color=COLOR_REL, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    ax.annotate('', xy=(9.0, 2.3), xytext=(12.5, 5.5), arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5, connectionstyle='arc3,rad=0.2'))
    ax.text(12.0, 4.0, '1:N', fontsize=12, fontweight='bold', color=COLOR_REL, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    ax.annotate('', xy=(10.5, 1.8), xytext=(9.5, 2.0), arrowprops=dict(arrowstyle='->', color=COLOR_REL, lw=2.5))
    ax.text(10.0, 2.3, '1:N', fontsize=11, fontweight='bold', color=COLOR_REL, ha='center', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_REL, alpha=0.9))

    # ===== TEXTOS =====
    ax.text(8, 9.7, 'Modelo Entidad-Relación — Caso SUNBURST', ha='center', va='center', fontsize=18, fontweight='bold', color=COLOR_HEADER, fontfamily='sans-serif')
    ax.text(8, 9.25, 'Análisis de Gestión de Datos | SolarWinds Orion Platform', ha='center', va='center', fontsize=11, color='#666666', style='italic')

    legend_y = 4.5
    legend_x = 0.6
    ax.text(legend_x, legend_y, 'Leyenda:', fontsize=10, fontweight='bold', color='#333')
    for i, (color, label) in enumerate([(COLOR_PK, 'Clave Primaria (PK)'), (COLOR_FK, 'Clave Foránea (FK)'), (COLOR_ATTR, 'Atributo'), ('#ffffff', 'Línea roja = Relación')]):
        rect = plt.Rectangle((legend_x, legend_y - 0.42*(i+1)), 0.3, 0.25, facecolor=color, edgecolor='#999', linewidth=0.5)
        ax.add_patch(rect)
        ax.text(legend_x + 0.45, legend_y - 0.42*(i+1) + 0.12, label, fontsize=8.5, va='center', color='#555')

    plt.tight_layout()
    filepath = ruta + 'ER.png'
    plt.savefig(filepath, dpi=180, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    ✓ Diagrama ER guardado → {filepath}")

if __name__ == '__main__':
    clientes = generar_clientes()
    versiones = generar_versiones()
    instalaciones = generar_instalaciones(clientes, versiones)
    generar_diagrama_er()
    
    # Guardar usando Pandas directamente
    clientes.to_csv('data/clientes.csv', index=False)
    versiones.to_csv('data/versiones_software.csv', index=False)
    instalaciones.to_csv('data/instalaciones.csv', index=False)
    print("\n[ROL1] CSVs guardados exitosamente en la carpeta data/")
