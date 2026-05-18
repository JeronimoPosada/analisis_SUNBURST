"""
=============================================================================
ROL 2: Analista de Calidad - Validación y Detección de Patrones
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

Este script valida la calidad de los datos generados por el Rol 1,
genera eventos de seguridad, detecta anomalías y crea visualizaciones.

Métricas DAMA DMBOK implementadas:
  - Completitud: porcentaje de campos no nulos
  - Exactitud: valores dentro de rangos válidos
  - Consistencia: integridad referencial y coherencia de fechas

Uso:
    python rol2_calidad_datos.py
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para guardar PNGs
import seaborn as sns
import os
from datetime import datetime, timedelta

# Configuración de reproducibilidad
np.random.seed(42)

# Configuración global de estilo para gráficos
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'figure.facecolor': 'white',
    'axes.facecolor': '#f8f9fa',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# Paleta de colores profesional
COLORES = {
    'primario': '#1a73e8',
    'secundario': '#ea4335',
    'exito': '#34a853',
    'alerta': '#fbbc04',
    'critico': '#d93025',
    'neutro': '#5f6368',
    'fondo_claro': '#e8f0fe',
}

# ===========================================================================
# CONSTANTES PARA VALIDACIÓN
# ===========================================================================

TIPOS_EVENTO = [
    'acceso_normal', 'descarga_datos', 'escalamiento_privilegios',
    'conexion_c2', 'exfiltracion', 'reconocimiento', 'movimiento_lateral',
    'persistencia', 'alerta_ids', 'modificacion_logs'
]

SEVERIDADES = ['Baja', 'Media', 'Alta', 'Crítica']

FECHA_MIN = datetime(2019, 1, 1)
FECHA_MAX = datetime(2021, 6, 30)

TIPOS_ORG_VALIDOS = [
    'Gobierno Federal', 'Gobierno Estatal', 'Empresa Privada',
    'Institución Educativa', 'Organización de Salud', 'ONG'
]

SECTORES_VALIDOS = [
    'Tecnología', 'Defensa', 'Energía', 'Finanzas',
    'Telecomunicaciones', 'Salud', 'Gobierno', 'Educación'
]

CRITICIDADES_VALIDAS = ['Alta', 'Media', 'Baja']
NIVELES_SENSIBLES_VALIDOS = ['Bajo', 'Medio', 'Alto', 'Crítico']


# ===========================================================================
# FUNCIONES DE VALIDACIÓN
# ===========================================================================

def validar_datos(clientes_df, versiones_df, instalaciones_df):
    """
    Valida la calidad de los datos generados por el Rol 1.
    Verifica integridad referencial, nulos, duplicados y rangos de datos.

    Parámetros:
        clientes_df (pd.DataFrame): DataFrame de clientes
        versiones_df (pd.DataFrame): DataFrame de versiones
        instalaciones_df (pd.DataFrame): DataFrame de instalaciones

    Retorna:
        dict: Diccionario con los resultados de validación por categoría
    """
    print("[ROL2] Validando datos...")
    resultados = {}

    # 1. Verificar nulos
    print("    → Verificando valores nulos...")
    nulos = {
        'clientes': clientes_df.isnull().sum().to_dict(),
        'versiones_software': versiones_df.isnull().sum().to_dict(),
        'instalaciones': instalaciones_df.isnull().sum().to_dict()
    }
    total_nulos = sum(sum(v.values()) for v in nulos.values())
    resultados['nulos'] = nulos
    print(f"      Total de valores nulos: {total_nulos}")

    # 2. Verificar duplicados
    print("    → Verificando duplicados...")
    duplicados = {
        'clientes_id_duplicados': clientes_df['cliente_id'].duplicated().sum(),
        'versiones_id_duplicados': versiones_df['version_id'].duplicated().sum(),
        'instalaciones_id_duplicados': instalaciones_df['instalacion_id'].duplicated().sum()
    }
    resultados['duplicados'] = duplicados
    print(f"      IDs duplicados: clientes={duplicados['clientes_id_duplicados']}, "
          f"versiones={duplicados['versiones_id_duplicados']}, "
          f"instalaciones={duplicados['instalaciones_id_duplicados']}")

    # 3. Verificar integridad referencial
    print("    → Verificando integridad referencial...")
    clientes_ids_validos = set(clientes_df['cliente_id'].tolist())
    versiones_ids_validos = set(versiones_df['version_id'].tolist())

    fk_clientes_invalidos = instalaciones_df[
        ~instalaciones_df['cliente_id'].isin(clientes_ids_validos)
    ].shape[0]
    fk_versiones_invalidos = instalaciones_df[
        ~instalaciones_df['version_id'].isin(versiones_ids_validos)
    ].shape[0]

    resultados['integridad_referencial'] = {
        'fk_clientes_invalidos': fk_clientes_invalidos,
        'fk_versiones_invalidos': fk_versiones_invalidos
    }
    print(f"      FK clientes inválidos: {fk_clientes_invalidos}")
    print(f"      FK versiones inválidos: {fk_versiones_invalidos}")

    # 4. Verificar rangos de fechas
    print("    → Verificando rangos de fechas...")
    fechas_instalacion = pd.to_datetime(instalaciones_df['fecha_instalacion'])
    fuera_rango = fechas_instalacion[
        (fechas_instalacion < FECHA_MIN) | (fechas_instalacion > FECHA_MAX)
    ].shape[0]
    resultados['fechas_fuera_rango'] = fuera_rango
    print(f"      Fechas fuera de rango (2019-2021): {fuera_rango}")

    # 5. Verificar valores de categorías
    print("    → Verificando valores categóricos...")
    tipo_org_invalidos = clientes_df[~clientes_df['tipo_org'].isin(TIPOS_ORG_VALIDOS)].shape[0]
    sector_invalidos = clientes_df[~clientes_df['sector'].isin(SECTORES_VALIDOS)].shape[0]
    criticidad_invalidos = clientes_df[~clientes_df['criticidad'].isin(CRITICIDADES_VALIDAS)].shape[0]
    nivel_invalidos = instalaciones_df[
        ~instalaciones_df['nivel_datos_sensibles'].isin(NIVELES_SENSIBLES_VALIDOS)
    ].shape[0]

    resultados['categorias_invalidas'] = {
        'tipo_org': tipo_org_invalidos,
        'sector': sector_invalidos,
        'criticidad': criticidad_invalidos,
        'nivel_datos_sensibles': nivel_invalidos
    }
    print(f"      Categorías inválidas: tipo_org={tipo_org_invalidos}, "
          f"sector={sector_invalidos}, criticidad={criticidad_invalidos}, "
          f"nivel_sensibles={nivel_invalidos}")

    print("    ✓ Validación completada")
    return resultados


def calcular_metricas_dama(clientes_df, versiones_df, instalaciones_df):
    """
    Calcula métricas de calidad de datos según el marco DAMA DMBOK.
    Implementa 3 métricas principales: Completitud, Exactitud y Consistencia.

    Parámetros:
        clientes_df (pd.DataFrame): DataFrame de clientes
        versiones_df (pd.DataFrame): DataFrame de versiones
        instalaciones_df (pd.DataFrame): DataFrame de instalaciones

    Retorna:
        pd.DataFrame: DataFrame con columnas:
            - tabla, columna, metrica, valor_actual, umbral, estado
    """
    print("\n[ROL2] Calculando métricas DAMA DMBOK...")
    reportes = []

    dataframes = {
        'clientes': clientes_df,
        'versiones_software': versiones_df,
        'instalaciones': instalaciones_df
    }

    for nombre_tabla, df in dataframes.items():
        print(f"    → Evaluando tabla: {nombre_tabla}")

        for columna in df.columns:
            # --- COMPLETITUD ---
            # Fórmula: (registros_no_nulos / total_registros) * 100
            total = len(df)
            no_nulos = df[columna].notna().sum()
            completitud = round((no_nulos / total) * 100, 2)
            umbral_completitud = 95.0
            estado_completitud = 'APROBADO' if completitud >= umbral_completitud else 'FALLIDO'

            reportes.append({
                'tabla': nombre_tabla,
                'columna': columna,
                'metrica': 'Completitud',
                'valor_actual': completitud,
                'umbral': umbral_completitud,
                'estado': estado_completitud
            })

            # --- EXACTITUD ---
            # Depende del tipo de columna
            if df[columna].dtype == 'object':
                # Para strings: verificar que no estén vacíos y tengan longitud razonable
                vacios = (df[columna].str.strip() == '').sum() if df[columna].notna().any() else 0
                exactitud = round(((total - vacios) / total) * 100, 2)
            elif pd.api.types.is_numeric_dtype(df[columna]):
                # Para numéricos: verificar que sean positivos (IDs)
                if '_id' in columna:
                    positivos = (df[columna] > 0).sum()
                    exactitud = round((positivos / total) * 100, 2)
                else:
                    exactitud = 100.0  # Otros numéricos se asumen correctos
            elif pd.api.types.is_bool_dtype(df[columna]):
                exactitud = 100.0  # Booleanos siempre son válidos
            else:
                exactitud = 100.0

            umbral_exactitud = 90.0
            estado_exactitud = 'APROBADO' if exactitud >= umbral_exactitud else 'FALLIDO'

            reportes.append({
                'tabla': nombre_tabla,
                'columna': columna,
                'metrica': 'Exactitud',
                'valor_actual': exactitud,
                'umbral': umbral_exactitud,
                'estado': estado_exactitud
            })

    # --- CONSISTENCIA (a nivel de relaciones entre tablas) ---
    print("    → Evaluando consistencia entre tablas...")

    # Consistencia FK: cliente_id en instalaciones → clientes
    clientes_ids = set(clientes_df['cliente_id'].tolist())
    fk_clientes_validos = instalaciones_df['cliente_id'].isin(clientes_ids).sum()
    consistencia_clientes = round((fk_clientes_validos / len(instalaciones_df)) * 100, 2)

    reportes.append({
        'tabla': 'instalaciones',
        'columna': 'cliente_id (FK)',
        'metrica': 'Consistencia',
        'valor_actual': consistencia_clientes,
        'umbral': 100.0,
        'estado': 'APROBADO' if consistencia_clientes == 100.0 else 'FALLIDO'
    })

    # Consistencia FK: version_id en instalaciones → versiones
    versiones_ids = set(versiones_df['version_id'].tolist())
    fk_versiones_validos = instalaciones_df['version_id'].isin(versiones_ids).sum()
    consistencia_versiones = round((fk_versiones_validos / len(instalaciones_df)) * 100, 2)

    reportes.append({
        'tabla': 'instalaciones',
        'columna': 'version_id (FK)',
        'metrica': 'Consistencia',
        'valor_actual': consistencia_versiones,
        'umbral': 100.0,
        'estado': 'APROBADO' if consistencia_versiones == 100.0 else 'FALLIDO'
    })

    # Consistencia temporal: fecha_instalacion >= fecha_release de la versión
    instalaciones_merge = instalaciones_df.merge(
        versiones_df[['version_id', 'fecha_release']],
        on='version_id',
        how='left'
    )
    fechas_inst = pd.to_datetime(instalaciones_merge['fecha_instalacion'])
    fechas_rel = pd.to_datetime(instalaciones_merge['fecha_release'])
    fechas_coherentes = (fechas_inst >= fechas_rel).sum()
    consistencia_fechas = round((fechas_coherentes / len(instalaciones_df)) * 100, 2)

    reportes.append({
        'tabla': 'instalaciones',
        'columna': 'fecha_instalacion vs fecha_release',
        'metrica': 'Consistencia',
        'valor_actual': consistencia_fechas,
        'umbral': 100.0,
        'estado': 'APROBADO' if consistencia_fechas == 100.0 else 'FALLIDO'
    })

    reporte_df = pd.DataFrame(reportes)

    # Resumen
    aprobados = reporte_df[reporte_df['estado'] == 'APROBADO'].shape[0]
    total_metricas = len(reporte_df)
    print(f"    ✓ {total_metricas} métricas calculadas: {aprobados} APROBADAS, "
          f"{total_metricas - aprobados} FALLIDAS")

    return reporte_df


def detectar_anomalias(instalaciones_df, eventos_df, versiones_df):
    """
    Detecta patrones anómalos en los datos, incluyendo:
    - Fechas fuera de rango
    - Concentraciones inusuales de eventos
    - Simulación del problema 18,000 vs <100

    Parámetros:
        instalaciones_df (pd.DataFrame): DataFrame de instalaciones
        eventos_df (pd.DataFrame): DataFrame de eventos de seguridad
        versiones_df (pd.DataFrame): DataFrame de versiones

    Retorna:
        dict: Diccionario con anomalías detectadas
    """
    print("\n[ROL2] Detectando anomalías...")
    anomalias = {}

    # 1. Anomalía temporal: instalaciones con fechas sospechosas
    print("    → Buscando anomalías temporales...")
    fechas = pd.to_datetime(instalaciones_df['fecha_instalacion'])
    q1 = fechas.quantile(0.25)
    q3 = fechas.quantile(0.75)
    # Se usa el rango para identificar instalaciones atípicas por fecha
    anomalias['fechas_extremas'] = {
        'mas_antigua': str(fechas.min()),
        'mas_reciente': str(fechas.max()),
        'rango_dias': (fechas.max() - fechas.min()).days
    }

    # 2. Anomalía en eventos: detección de eventos anómalos
    print("    → Analizando eventos anómalos...")
    eventos_anomalos = eventos_df[eventos_df['es_anomalo'] == True]
    anomalias['eventos_anomalos'] = {
        'total_eventos': len(eventos_df),
        'eventos_anomalos': len(eventos_anomalos),
        'porcentaje_anomalo': round(len(eventos_anomalos) / len(eventos_df) * 100, 2),
        'tipos_evento_anomalo': eventos_anomalos['tipo_evento'].value_counts().to_dict()
    }
    print(f"      Eventos anómalos: {len(eventos_anomalos)}/{len(eventos_df)} "
          f"({anomalias['eventos_anomalos']['porcentaje_anomalo']}%)")

    # 3. Simulación 18,000 vs <100
    print("    → Simulando filtrado 18,000 → <100...")
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()

    # Paso 1: Total de instalaciones con versiones afectadas (simula las 18,000)
    instalaciones_afectadas = instalaciones_df[
        instalaciones_df['version_id'].isin(versiones_sunburst)
    ]

    # Paso 2: Filtrar por los que tuvieron eventos de seguridad
    ids_con_eventos = set(eventos_df['instalacion_id'].tolist())
    con_eventos = instalaciones_afectadas[
        instalaciones_afectadas['instalacion_id'].isin(ids_con_eventos)
    ]

    # Paso 3: Filtrar por solo eventos anómalos (realmente comprometidos)
    ids_anomalos = set(eventos_anomalos['instalacion_id'].tolist())
    realmente_comprometidos = instalaciones_afectadas[
        instalaciones_afectadas['instalacion_id'].isin(ids_anomalos)
    ]

    # Clientes únicos comprometidos
    clientes_comprometidos = realmente_comprometidos['cliente_id'].nunique()

    anomalias['cascada_filtrado'] = {
        'paso1_total_instalaciones': len(instalaciones_df),
        'paso2_versiones_sunburst': len(instalaciones_afectadas),
        'paso3_con_eventos': len(con_eventos),
        'paso4_realmente_comprometidos': len(realmente_comprometidos),
        'clientes_unicos_comprometidos': clientes_comprometidos
    }

    print(f"      Total instalaciones: {len(instalaciones_df)}")
    print(f"      Con versiones SUNBURST: {len(instalaciones_afectadas)}")
    print(f"      Con eventos de seguridad: {len(con_eventos)}")
    print(f"      Realmente comprometidos: {len(realmente_comprometidos)}")
    print(f"      Clientes únicos comprometidos: {clientes_comprometidos}")

    print("    ✓ Detección de anomalías completada")
    return anomalias


def generar_eventos_seguridad(instalaciones_df, versiones_df, n=200):
    """
    Genera un DataFrame de eventos de seguridad que simula la actividad
    del malware SUNBURST en las instalaciones afectadas.

    Solo ~5% de los eventos son anómalos (coherente con <100 de 18,000).
    Los eventos anómalos se concentran en instalaciones con versiones SUNBURST.

    Parámetros:
        instalaciones_df (pd.DataFrame): DataFrame de instalaciones
        versiones_df (pd.DataFrame): DataFrame de versiones
        n (int): Número de eventos a generar. Por defecto 200.

    Retorna:
        pd.DataFrame: DataFrame con columnas:
            - evento_id, instalacion_id, timestamp, tipo_evento, severidad, es_anomalo
    """
    print(f"\n[ROL2] Generando {n} eventos de seguridad...")

    # Identificar instalaciones con versiones SUNBURST
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    instalaciones_sunburst = instalaciones_df[
        instalaciones_df['version_id'].isin(versiones_sunburst)
    ]['instalacion_id'].tolist()

    instalaciones_limpias = instalaciones_df[
        ~instalaciones_df['version_id'].isin(versiones_sunburst)
    ]['instalacion_id'].tolist()

    eventos = []
    for i in range(1, n + 1):
        # 80% de eventos en instalaciones SUNBURST, 20% en limpias
        if np.random.random() < 0.80 and len(instalaciones_sunburst) > 0:
            instalacion_id = np.random.choice(instalaciones_sunburst)
        else:
            instalacion_id = np.random.choice(
                instalaciones_limpias if len(instalaciones_limpias) > 0 else instalaciones_sunburst
            )

        # Determinar si el evento es anómalo (~5% del total)
        # Los eventos anómalos solo ocurren en instalaciones SUNBURST
        es_anomalo = False
        if instalacion_id in instalaciones_sunburst and np.random.random() < 0.065:
            es_anomalo = True

        # Tipo de evento: los anómalos tienden a ser más severos
        if es_anomalo:
            tipo_evento = np.random.choice(
                ['conexion_c2', 'exfiltracion', 'escalamiento_privilegios',
                 'movimiento_lateral', 'modificacion_logs'],
                p=[0.30, 0.25, 0.20, 0.15, 0.10]
            )
            severidad = np.random.choice(SEVERIDADES, p=[0.05, 0.10, 0.40, 0.45])
        else:
            tipo_evento = np.random.choice(
                TIPOS_EVENTO,
                p=[0.35, 0.15, 0.05, 0.02, 0.01, 0.15, 0.05, 0.05, 0.12, 0.05]
            )
            severidad = np.random.choice(SEVERIDADES, p=[0.50, 0.30, 0.15, 0.05])

        # Timestamp: entre la fecha de instalación y marzo 2021
        inst_row = instalaciones_df[
            instalaciones_df['instalacion_id'] == instalacion_id
        ].iloc[0]
        fecha_base = pd.to_datetime(inst_row['fecha_instalacion'])
        fecha_fin = datetime(2021, 3, 31)
        dias_rango = max((fecha_fin - fecha_base).days, 1)
        offset_dias = np.random.randint(0, dias_rango)
        timestamp = fecha_base + timedelta(
            days=int(offset_dias),
            hours=int(np.random.randint(0, 24)),
            minutes=int(np.random.randint(0, 60)),
            seconds=int(np.random.randint(0, 60))
        )

        eventos.append({
            'evento_id': i,
            'instalacion_id': instalacion_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'tipo_evento': tipo_evento,
            'severidad': severidad,
            'es_anomalo': es_anomalo
        })

    df = pd.DataFrame(eventos)
    anomalos = df['es_anomalo'].sum()
    print(f"    ✓ {len(df)} eventos generados ({anomalos} anómalos, "
          f"{round(anomalos/len(df)*100, 1)}%)")
    return df


def crear_graficos(eventos_df, reporte_df, instalaciones_df, versiones_df, clientes_df,
                   ruta='../visualizations/'):
    """
    Genera 5 visualizaciones profesionales para el análisis de calidad.

    Gráficos generados:
        1. anomalias.png - Distribución de eventos anómalos vs normales
        2. severidad_eventos.png - Distribución de severidad de eventos
        3. clientes_afectados.png - Análisis de clientes por criticidad y afectación
        4. calidad_datos.png - Heatmap de métricas de calidad por tabla/columna
        5. grafico_cascada.png - Filtrado progresivo 18,000 → <100

    Parámetros:
        eventos_df, reporte_df, instalaciones_df, versiones_df, clientes_df: DataFrames
        ruta (str): Carpeta destino para los PNGs
    """
    os.makedirs(ruta, exist_ok=True)
    print(f"\n[ROL2] Generando visualizaciones en {ruta}...")

    # =========================================================
    # GRÁFICO 1: Anomalías detectadas
    # =========================================================
    print("    → 1/5: anomalias.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1a. Pie chart: proporción anómalos vs normales
    anomalos = eventos_df['es_anomalo'].value_counts()
    labels = ['Normal', 'Anómalo']
    colors = [COLORES['primario'], COLORES['critico']]
    explode = (0, 0.1)
    axes[0].pie(
        [anomalos.get(False, 0), anomalos.get(True, 0)],
        labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', shadow=True, startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    axes[0].set_title('Proporción de Eventos\nAnómalos vs Normales', fontweight='bold')

    # 1b. Bar chart: tipos de evento en anómalos
    eventos_anomalos = eventos_df[eventos_df['es_anomalo'] == True]
    if len(eventos_anomalos) > 0:
        tipo_counts = eventos_anomalos['tipo_evento'].value_counts()
        barras = axes[1].barh(tipo_counts.index, tipo_counts.values, color=COLORES['critico'], alpha=0.8)
        axes[1].set_xlabel('Cantidad de Eventos')
        axes[1].set_title('Tipos de Eventos Anómalos', fontweight='bold')
        for barra in barras:
            width = barra.get_width()
            axes[1].text(width + 0.1, barra.get_y() + barra.get_height()/2,
                        f'{int(width)}', ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'anomalias.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # GRÁFICO 2: Severidad de eventos
    # =========================================================
    print("    → 2/5: severidad_eventos.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 2a. Barras agrupadas: severidad por tipo de anomalía
    sev_order = ['Baja', 'Media', 'Alta', 'Crítica']
    colores_sev = ['#34a853', '#fbbc04', '#ea4335', '#d93025']

    for idx, (anomalo_val, label, ax) in enumerate([
        (False, 'Eventos Normales', axes[0]),
        (True, 'Eventos Anómalos', axes[1])
    ]):
        subset = eventos_df[eventos_df['es_anomalo'] == anomalo_val]
        if len(subset) > 0:
            sev_counts = subset['severidad'].value_counts().reindex(sev_order, fill_value=0)
            bars = ax.bar(sev_counts.index, sev_counts.values, color=colores_sev, edgecolor='white', linewidth=1.5)
            ax.set_title(f'Severidad: {label}', fontweight='bold')
            ax.set_ylabel('Cantidad')
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, height + 0.5,
                           f'{int(height)}', ha='center', va='bottom', fontweight='bold')

    plt.suptitle('Distribución de Severidad de Eventos de Seguridad',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'severidad_eventos.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # GRÁFICO 3: Clientes afectados
    # =========================================================
    print("    → 3/5: clientes_afectados.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 3a. Distribución de clientes por criticidad
    crit_counts = clientes_df['criticidad'].value_counts().reindex(
        ['Alta', 'Media', 'Baja'], fill_value=0
    )
    colors_crit = [COLORES['critico'], COLORES['alerta'], COLORES['exito']]
    bars = axes[0].bar(crit_counts.index, crit_counts.values, color=colors_crit,
                       edgecolor='white', linewidth=1.5)
    axes[0].set_title('Clientes por Nivel de Criticidad', fontweight='bold')
    axes[0].set_ylabel('Cantidad de Clientes')
    for bar in bars:
        height = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2, height + 0.3,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=13)

    # 3b. Sectores de clientes
    sector_counts = clientes_df['sector'].value_counts()
    axes[1].barh(sector_counts.index, sector_counts.values,
                 color=sns.color_palette('Blues_d', len(sector_counts)))
    axes[1].set_xlabel('Cantidad de Clientes')
    axes[1].set_title('Distribución por Sector', fontweight='bold')
    for i, (val, name) in enumerate(zip(sector_counts.values, sector_counts.index)):
        axes[1].text(val + 0.2, i, f'{val}', ha='left', va='center', fontweight='bold')

    plt.suptitle('Análisis de Clientes Afectados por SUNBURST',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'clientes_afectados.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # GRÁFICO 4: Calidad de datos (heatmap)
    # =========================================================
    print("    → 4/5: calidad_datos.png")
    fig, ax = plt.subplots(figsize=(12, 8))

    # Crear pivot table para el heatmap
    pivot_data = reporte_df.pivot_table(
        index=['tabla', 'columna'],
        columns='metrica',
        values='valor_actual',
        aggfunc='first'
    )

    # Crear labels legibles
    labels = [f"{tabla}\n{col}" for tabla, col in pivot_data.index]

    sns.heatmap(
        pivot_data.values,
        xticklabels=pivot_data.columns,
        yticklabels=labels,
        annot=True, fmt='.1f',
        cmap='RdYlGn', vmin=80, vmax=100,
        linewidths=0.5, linecolor='white',
        cbar_kws={'label': 'Porcentaje (%)'},
        ax=ax
    )
    ax.set_title('Métricas de Calidad de Datos (DAMA DMBOK)\nCompletitud, Exactitud y Consistencia',
                 fontweight='bold', fontsize=14)
    ax.set_ylabel('')

    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'calidad_datos.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # GRÁFICO 5: Cascada (18,000 → <100)
    # =========================================================
    print("    → 5/5: grafico_cascada.png")
    fig, ax = plt.subplots(figsize=(12, 7))

    # Simular la cascada del caso real adaptada a nuestros datos
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    inst_sunburst = instalaciones_df[instalaciones_df['version_id'].isin(versiones_sunburst)]

    ids_con_eventos_anomalos = set(
        eventos_df[eventos_df['es_anomalo'] == True]['instalacion_id'].tolist()
    )
    inst_comprometidas = inst_sunburst[
        inst_sunburst['instalacion_id'].isin(ids_con_eventos_anomalos)
    ]
    clientes_unic_comp = inst_comprometidas['cliente_id'].nunique()

    # Datos de la cascada (mezcla de escala real y datos sintéticos)
    etapas = [
        'Total Descargas\nActivadas\n(Caso Real)',
        'Versiones con\nSUNBURST\n(Caso Real)',
        'Instalaciones\nSimuladas\n(Datos Sintéticos)',
        'Con Versiones\nSUNBURST\n(Datos Sintéticos)',
        'Realmente\nComprometidos\n(Datos Sintéticos)',
        'Clientes\nÚnicos\nComprometidos'
    ]
    valores = [18000, 18000, len(instalaciones_df), len(inst_sunburst),
               len(inst_comprometidas), clientes_unic_comp]

    colores_cascada = ['#1a73e8', '#4285f4', '#5f6368', '#ea4335', '#d93025', '#b71c1c']

    bars = ax.bar(range(len(etapas)), valores, color=colores_cascada,
                  edgecolor='white', linewidth=2, width=0.6)

    # Etiquetas sobre las barras
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                f'{val:,}', ha='center', va='bottom',
                fontweight='bold', fontsize=13, color='#333')

    ax.set_xticks(range(len(etapas)))
    ax.set_xticklabels(etapas, fontsize=9)
    ax.set_ylabel('Número de Instalaciones / Clientes', fontsize=12)
    ax.set_title('Gráfico de Cascada: De 18,000 Descargas a <100 Comprometidos\n'
                 'Filtrado Progresivo del Incidente SUNBURST',
                 fontweight='bold', fontsize=14)

    # Línea divisoria entre datos reales y sintéticos
    ax.axvline(x=1.5, color='gray', linestyle='--', alpha=0.5)
    ax.text(0.5, max(valores) * 0.9, 'Caso Real', ha='center',
            fontsize=10, style='italic', color='gray')
    ax.text(3.5, max(valores) * 0.9, 'Datos Sintéticos', ha='center',
            fontsize=10, style='italic', color='gray')

    # Flechas de reducción
    for i in range(len(valores) - 1):
        if valores[i] > valores[i+1]:
            reduccion = round((1 - valores[i+1]/valores[i]) * 100, 1)
            mid_y = (valores[i] + valores[i+1]) / 2
            ax.annotate(f'-{reduccion}%',
                       xy=(i + 0.5, mid_y),
                       fontsize=9, color=COLORES['critico'],
                       fontweight='bold', ha='center')

    ax.set_ylim(0, max(valores) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'grafico_cascada.png'), dpi=150, bbox_inches='tight')
    plt.close()

    print("    ✓ 5 gráficos generados exitosamente")


def guardar_csvs_rol2(eventos_df, reporte_df, ruta='../data/'):
    """
    Guarda los DataFrames del Rol 2 como archivos CSV.

    Parámetros:
        eventos_df (pd.DataFrame): DataFrame de eventos de seguridad
        reporte_df (pd.DataFrame): DataFrame de reporte de calidad
        ruta (str): Carpeta destino
    """
    os.makedirs(ruta, exist_ok=True)

    archivos = {
        'eventos_seguridad.csv': eventos_df,
        'reporte_calidad.csv': reporte_df
    }

    print("\n[ROL2] Guardando archivos CSV...")
    for nombre, df in archivos.items():
        filepath = os.path.join(ruta, nombre)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"    ✓ {nombre} guardado ({len(df)} registros) → {filepath}")


# ===========================================================================
# EJECUCIÓN PRINCIPAL
# ===========================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  ROL 2: ANÁLISIS DE CALIDAD DE DATOS - CASO SUNBURST")
    print("=" * 70)
    print()

    # Determinar rutas relativas al script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    vis_dir = os.path.join(script_dir, '..', 'visualizations')

    # 1. Cargar datos del Rol 1
    print("[ROL2] Cargando datos del Rol 1...")
    clientes = pd.read_csv(os.path.join(data_dir, 'clientes.csv'))
    versiones = pd.read_csv(os.path.join(data_dir, 'versiones_software.csv'))
    instalaciones = pd.read_csv(os.path.join(data_dir, 'instalaciones.csv'))
    print(f"    ✓ Cargados: {len(clientes)} clientes, {len(versiones)} versiones, "
          f"{len(instalaciones)} instalaciones")

    # 2. Validar datos
    print()
    resultados_validacion = validar_datos(clientes, versiones, instalaciones)

    # 3. Calcular métricas DAMA
    reporte_calidad = calcular_metricas_dama(clientes, versiones, instalaciones)

    # 4. Generar eventos de seguridad
    eventos = generar_eventos_seguridad(instalaciones, versiones, n=200)

    # 5. Detectar anomalías
    anomalias = detectar_anomalias(instalaciones, eventos, versiones)

    # 6. Crear gráficos
    crear_graficos(eventos, reporte_calidad, instalaciones, versiones, clientes, ruta=vis_dir)

    # 7. Guardar CSVs
    guardar_csvs_rol2(eventos, reporte_calidad, ruta=data_dir)

    # 8. Resumen final
    print()
    print("=" * 70)
    print("  RESUMEN FINAL - ROL 2")
    print("=" * 70)
    print(f"  • Métricas DAMA evaluadas: {len(reporte_calidad)}")
    print(f"  • Métricas APROBADAS: {(reporte_calidad['estado'] == 'APROBADO').sum()}")
    print(f"  • Métricas FALLIDAS: {(reporte_calidad['estado'] == 'FALLIDO').sum()}")
    print(f"  • Eventos generados: {len(eventos)}")
    print(f"  • Eventos anómalos: {eventos['es_anomalo'].sum()}")
    print(f"  • Gráficos generados: 5")
    print(f"  • CSVs guardados: 2")
    print("=" * 70)
    print("\n[ROL2] ¡Análisis de calidad completado exitosamente!")
