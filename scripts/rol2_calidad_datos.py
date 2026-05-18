"""
=============================================================================
ROL 2: Analista de Calidad - Validación y Detección de Patrones
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

Este script valida la calidad, genera eventos y crea las 5 visualizaciones
avanzadas de anomalías. Implementa DAMA DMBOK.
Uso:
    python scripts/rol2_calidad_datos.py
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de reproducibilidad
np.random.seed(42)

# Estilo profesional para gráficos
plt.rcParams.update({
    'figure.figsize': (10, 6), 'font.size': 11, 'axes.titlesize': 14,
    'axes.labelsize': 12, 'figure.facecolor': 'white', 'axes.facecolor': '#f8f9fa',
    'axes.grid': True, 'grid.alpha': 0.3,
})

COLORES = {'primario': '#1a73e8', 'secundario': '#ea4335', 'exito': '#34a853',
           'alerta': '#fbbc04', 'critico': '#d93025', 'neutro': '#5f6368'}

TIPOS_EVENTO = ['acceso_normal', 'descarga_datos', 'escalamiento_privilegios',
    'conexion_c2', 'exfiltracion', 'reconocimiento', 'movimiento_lateral',
    'persistencia', 'alerta_ids', 'modificacion_logs']

SEVERIDADES = ['Baja', 'Media', 'Alta', 'Crítica']

# Reemplazamos OS/Datetime con Pandas puro
FECHA_MIN = pd.to_datetime('2019-01-01')
FECHA_MAX = pd.to_datetime('2021-06-30')

TIPOS_ORG_VALIDOS = ['Gobierno Federal', 'Gobierno Estatal', 'Empresa Privada',
    'Institución Educativa', 'Organización de Salud', 'ONG']

SECTORES_VALIDOS = ['Tecnología', 'Defensa', 'Energía', 'Finanzas',
    'Telecomunicaciones', 'Salud', 'Gobierno', 'Educación']

CRITICIDADES_VALIDAS = ['Alta', 'Media', 'Baja']
NIVELES_SENSIBLES_VALIDOS = ['Bajo', 'Medio', 'Alto', 'Crítico']

def validar_datos(clientes_df, versiones_df, instalaciones_df):
    print("[ROL2] Validando datos (análisis crítico)...")
    resultados = {}
    problemas_criticos = 0
    problemas_advertencia = 0

    print("\n    [1/6] Verificando valores nulos...")
    nulos_detalle = {}
    for nombre, df in [('clientes', clientes_df), ('versiones_software', versiones_df), ('instalaciones', instalaciones_df)]:
        nulos_col = df.isnull().sum()
        nulos_col = nulos_col[nulos_col > 0]
        if len(nulos_col) > 0:
            nulos_detalle[nombre] = nulos_col.to_dict()
            for col, n in nulos_col.items():
                print(f"      ❌ {nombre}.{col}: {n} valores nulos")
                problemas_criticos += 1
        else:
            print(f"      ✅ {nombre}: sin valores nulos")
    resultados['nulos'] = nulos_detalle

    print("\n    [2/6] Verificando strings vacíos...")
    vacios_detalle = {}
    for nombre, df in [('clientes', clientes_df), ('versiones_software', versiones_df), ('instalaciones', instalaciones_df)]:
        for col in df.select_dtypes(include='object').columns:
            vacios = (df[col].fillna('').str.strip() == '').sum() - df[col].isnull().sum()
            if vacios > 0:
                vacios_detalle[f'{nombre}.{col}'] = int(vacios)
                print(f"      ❌ {nombre}.{col}: {vacios} strings vacíos")
                problemas_advertencia += 1
    resultados['strings_vacios'] = vacios_detalle

    print("\n    [3/6] Verificando IDs duplicados...")
    for nombre, df, id_col in [('clientes', clientes_df, 'cliente_id'), ('versiones_software', versiones_df, 'version_id'), ('instalaciones', instalaciones_df, 'instalacion_id')]:
        dups = df[id_col].duplicated().sum()
        if dups > 0:
            ids_dup = df[df[id_col].duplicated(keep=False)][id_col].unique().tolist()
            print(f"      ❌ {nombre}.{id_col}: {dups} duplicados (IDs: {ids_dup})")
            problemas_criticos += 1
        else:
            print(f"      ✅ {nombre}.{id_col}: sin duplicados")

    print("\n    [4/6] Verificando integridad referencial...")
    clientes_ids = set(clientes_df['cliente_id'].tolist())
    versiones_ids = set(versiones_df['version_id'].tolist())

    fk_cli_inv = instalaciones_df[~instalaciones_df['cliente_id'].isin(clientes_ids)]
    fk_ver_inv = instalaciones_df[~instalaciones_df['version_id'].isin(versiones_ids)]

    if len(fk_cli_inv) > 0:
        ids_huerfanos = fk_cli_inv['cliente_id'].unique().tolist()
        print(f"      ❌ instalaciones.cliente_id: {len(fk_cli_inv)} FK huérfanas (IDs inexistentes: {ids_huerfanos})")
        problemas_criticos += 1
    else:
        print(f"      ✅ instalaciones.cliente_id: integridad OK")

    if len(fk_ver_inv) > 0:
        ids_huerfanos = fk_ver_inv['version_id'].unique().tolist()
        print(f"      ❌ instalaciones.version_id: {len(fk_ver_inv)} FK huérfanas (IDs inexistentes: {ids_huerfanos})")
        problemas_criticos += 1
    else:
        print(f"      ✅ instalaciones.version_id: integridad OK")

    print("\n    [5/6] Verificando fechas y consistencia temporal...")
    fechas_inst = pd.to_datetime(instalaciones_df['fecha_instalacion'], errors='coerce')
    fuera_rango = fechas_inst[(fechas_inst < FECHA_MIN) | (fechas_inst > FECHA_MAX)]
    if len(fuera_rango) > 0:
        print(f"      ❌ {len(fuera_rango)} fechas fuera del rango 2019-2021")
        problemas_criticos += 1
    else:
        print(f"      ✅ Todas las fechas dentro del rango")

    versiones_con_fecha = versiones_df.dropna(subset=['fecha_release'])
    inst_merge = instalaciones_df.merge(versiones_con_fecha[['version_id', 'fecha_release']], on='version_id', how='left')
    inst_merge['fecha_instalacion_dt'] = pd.to_datetime(inst_merge['fecha_instalacion'], errors='coerce')
    inst_merge['fecha_release_dt'] = pd.to_datetime(inst_merge['fecha_release'], errors='coerce')

    mask_valida = inst_merge['fecha_release_dt'].notna() & inst_merge['fecha_instalacion_dt'].notna()
    inconsistentes = inst_merge[mask_valida & (inst_merge['fecha_instalacion_dt'] < inst_merge['fecha_release_dt'])]

    if len(inconsistentes) > 0:
        print(f"      ❌ {len(inconsistentes)} instalaciones con fecha ANTERIOR al release")
        problemas_criticos += 1
    else:
        print(f"      ✅ Coherencia temporal OK")

    ver_sin_fecha = versiones_df[versiones_df['fecha_release'].isnull()]
    if len(ver_sin_fecha) > 0:
        print(f"      ⚠️  {len(ver_sin_fecha)} versiones sin fecha_release")
        problemas_advertencia += 1

    print("\n    [6/6] Verificando valores categóricos...")
    for col, validos in [('tipo_org', TIPOS_ORG_VALIDOS), ('sector', SECTORES_VALIDOS), ('criticidad', CRITICIDADES_VALIDAS)]:
        inv = clientes_df[clientes_df[col].notna() & ~clientes_df[col].isin(validos)]
        if len(inv) > 0:
            print(f"      ❌ clientes.{col}: {len(inv)} valores inválidos")
            problemas_advertencia += 1
        else:
            print(f"      ✅ clientes.{col}: valores válidos")

    inv_nivel = instalaciones_df[instalaciones_df['nivel_datos_sensibles'].notna() & ~instalaciones_df['nivel_datos_sensibles'].isin(NIVELES_SENSIBLES_VALIDOS)]
    if len(inv_nivel) > 0:
        print(f"      ❌ instalaciones.nivel_datos_sensibles: {len(inv_nivel)} valores inválidos")
        problemas_advertencia += 1

    print(f"\n    {'=' * 50}")
    print(f"    RESUMEN DE VALIDACIÓN:")
    print(f"    🔴 Problemas CRÍTICOS: {problemas_criticos}")
    print(f"    🟡 Advertencias: {problemas_advertencia}")
    print(f"    {'=' * 50}")
    
    return resultados

def calcular_metricas_dama(clientes_df, versiones_df, instalaciones_df):
    print("\n[ROL2] Calculando métricas DAMA DMBOK (análisis crítico)...")
    reportes = []
    dataframes = {'clientes': clientes_df, 'versiones_software': versiones_df, 'instalaciones': instalaciones_df}

    for nombre_tabla, df in dataframes.items():
        print(f"    → Evaluando tabla: {nombre_tabla}")
        for columna in df.columns:
            total = len(df)
            no_nulos = df[columna].notna().sum()

            if df[columna].dtype == 'object':
                vacios = df[columna].fillna('').apply(lambda x: str(x).strip() == '').sum()
                completitud_real = round(((total - vacios) / total) * 100, 2)
            else:
                completitud_real = round((no_nulos / total) * 100, 2)

            umbral_comp = 95.0
            estado_comp = 'APROBADO' if completitud_real >= umbral_comp else 'FALLIDO'
            reportes.append({'tabla': nombre_tabla, 'columna': columna, 'metrica': 'Completitud', 'valor_actual': completitud_real, 'umbral': umbral_comp, 'estado': estado_comp})

            exactitud = 100.0
            if df[columna].dtype == 'object':
                if columna == 'tipo_org':
                    exactitud = round((df[columna].isin(TIPOS_ORG_VALIDOS) | df[columna].isna()).sum() / total * 100, 2)
                elif columna == 'sector':
                    exactitud = round((df[columna].isin(SECTORES_VALIDOS) | df[columna].isna()).sum() / total * 100, 2)
                elif columna == 'criticidad':
                    exactitud = round((df[columna].isin(CRITICIDADES_VALIDAS) | df[columna].isna()).sum() / total * 100, 2)
                elif columna == 'nivel_datos_sensibles':
                    exactitud = round((df[columna].isin(NIVELES_SENSIBLES_VALIDOS) | df[columna].isna()).sum() / total * 100, 2)
                elif columna == 'pais':
                    exactitud = round(df[columna].fillna('').apply(lambda x: len(str(x).strip()) > 0).sum() / total * 100, 2)
                else:
                    exactitud = completitud_real
            elif pd.api.types.is_numeric_dtype(df[columna]) and '_id' in columna:
                exactitud = round((df[columna] > 0).sum() / total * 100, 2)
            elif not pd.api.types.is_numeric_dtype(df[columna]) and not pd.api.types.is_bool_dtype(df[columna]):
                exactitud = round((df[columna].notna().sum() / total) * 100, 2)

            umbral_exact = 90.0
            estado_exact = 'APROBADO' if exactitud >= umbral_exact else 'FALLIDO'
            reportes.append({'tabla': nombre_tabla, 'columna': columna, 'metrica': 'Exactitud', 'valor_actual': exactitud, 'umbral': umbral_exact, 'estado': estado_exact})

    print("    → Evaluando consistencia entre tablas...")
    
    # Consistencia FK
    fk_cli_val = instalaciones_df['cliente_id'].isin(set(clientes_df['cliente_id'].tolist())).sum()
    consist_cli = round((fk_cli_val / len(instalaciones_df)) * 100, 2)
    reportes.append({'tabla': 'instalaciones', 'columna': 'cliente_id (FK→clientes)', 'metrica': 'Consistencia', 'valor_actual': consist_cli, 'umbral': 100.0, 'estado': 'APROBADO' if consist_cli == 100.0 else 'FALLIDO'})

    fk_ver_val = instalaciones_df['version_id'].isin(set(versiones_df['version_id'].tolist())).sum()
    consist_ver = round((fk_ver_val / len(instalaciones_df)) * 100, 2)
    reportes.append({'tabla': 'instalaciones', 'columna': 'version_id (FK→versiones)', 'metrica': 'Consistencia', 'valor_actual': consist_ver, 'umbral': 100.0, 'estado': 'APROBADO' if consist_ver == 100.0 else 'FALLIDO'})

    # Coherencia temporal
    versiones_con_fecha = versiones_df.dropna(subset=['fecha_release'])
    inst_merge = instalaciones_df.merge(versiones_con_fecha[['version_id', 'fecha_release']], on='version_id', how='inner')
    if len(inst_merge) > 0:
        fechas_inst = pd.to_datetime(inst_merge['fecha_instalacion'], errors='coerce')
        fechas_rel = pd.to_datetime(inst_merge['fecha_release'], errors='coerce')
        mask = fechas_inst.notna() & fechas_rel.notna()
        coherentes = (fechas_inst[mask] >= fechas_rel[mask]).sum()
        total_comparables = mask.sum()
        consist_fecha = round((coherentes / total_comparables) * 100, 2) if total_comparables > 0 else 0.0
    else:
        consist_fecha = 0.0
    reportes.append({'tabla': 'instalaciones', 'columna': 'fecha_instalacion >= fecha_release', 'metrica': 'Consistencia', 'valor_actual': consist_fecha, 'umbral': 100.0, 'estado': 'APROBADO' if consist_fecha == 100.0 else 'FALLIDO'})

    fechas_all = pd.to_datetime(instalaciones_df['fecha_instalacion'], errors='coerce')
    en_rango = ((fechas_all >= FECHA_MIN) & (fechas_all <= FECHA_MAX)).sum()
    consist_rango = round((en_rango / len(instalaciones_df)) * 100, 2)
    reportes.append({'tabla': 'instalaciones', 'columna': 'fecha_instalacion (rango)', 'metrica': 'Consistencia', 'valor_actual': consist_rango, 'umbral': 100.0, 'estado': 'APROBADO' if consist_rango == 100.0 else 'FALLIDO'})

    for nombre, df, pk in [('clientes', clientes_df, 'cliente_id'), ('versiones_software', versiones_df, 'version_id'), ('instalaciones', instalaciones_df, 'instalacion_id')]:
        consist_pk = round((df[pk].nunique() / len(df)) * 100, 2)
        reportes.append({'tabla': nombre, 'columna': f'{pk} (unicidad PK)', 'metrica': 'Consistencia', 'valor_actual': consist_pk, 'umbral': 100.0, 'estado': 'APROBADO' if consist_pk == 100.0 else 'FALLIDO'})

    reporte_df = pd.DataFrame(reportes)
    aprobados = (reporte_df['estado'] == 'APROBADO').sum()
    fallidos = (reporte_df['estado'] == 'FALLIDO').sum()
    
    print(f"\n    {'=' * 50}")
    print(f"    RESULTADOS DAMA DMBOK:")
    print(f"    ✅ APROBADAS: {aprobados} | ❌ FALLIDAS: {fallidos}")
    print(f"    {'=' * 50}")

    return reporte_df

def detectar_anomalias(instalaciones_df, eventos_df, versiones_df, clientes_df):
    print("\n[ROL2] Detectando anomalías (análisis crítico)...")
    anomalias = {}
    
    eventos_anomalos = eventos_df[eventos_df['es_anomalo'] == True]
    print(f"    → Eventos anómalos encontrados: {len(eventos_anomalos)}/{len(eventos_df)}")
    
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    inst_afectadas = instalaciones_df[instalaciones_df['version_id'].isin(versiones_sunburst)]
    ids_anomalos = set(eventos_anomalos['instalacion_id'].tolist())
    comprometidos = inst_afectadas[inst_afectadas['instalacion_id'].isin(ids_anomalos)]
    clientes_comp = comprometidos[comprometidos['cliente_id'].isin(set(clientes_df['cliente_id'].tolist()))]['cliente_id'].nunique()

    anomalias['cascada'] = {
        'total_instalaciones': len(instalaciones_df),
        'con_sunburst': len(inst_afectadas),
        'comprometidos': len(comprometidos),
        'clientes_unicos': clientes_comp
    }

    print(f"    → Total: {len(instalaciones_df)} → SUNBURST: {len(inst_afectadas)} → Comprometidos: {len(comprometidos)} → Clientes U.: {clientes_comp}")
    return anomalias

def generar_eventos_seguridad(instalaciones_df, versiones_df, n=200):
    print(f"\n[ROL2] Generando {n} eventos de seguridad...")
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    inst_sunburst = instalaciones_df[instalaciones_df['version_id'].isin(versiones_sunburst)]['instalacion_id'].tolist()
    inst_limpias = instalaciones_df[~instalaciones_df['version_id'].isin(versiones_sunburst)]['instalacion_id'].tolist()

    if len(inst_limpias) == 0: inst_limpias = inst_sunburst
    eventos = []
    for i in range(1, n + 1):
        if np.random.random() < 0.80 and len(inst_sunburst) > 0:
            inst_id = np.random.choice(inst_sunburst)
        else:
            inst_id = np.random.choice(inst_limpias)

        es_anomalo = True if inst_id in inst_sunburst and np.random.random() < 0.065 else False
        if es_anomalo:
            tipo = np.random.choice(['conexion_c2', 'exfiltracion', 'escalamiento_privilegios', 'movimiento_lateral', 'modificacion_logs'], p=[0.30, 0.25, 0.20, 0.15, 0.10])
            sev = np.random.choice(SEVERIDADES, p=[0.05, 0.10, 0.40, 0.45])
        else:
            tipo = np.random.choice(TIPOS_EVENTO, p=[0.35, 0.15, 0.05, 0.02, 0.01, 0.15, 0.05, 0.05, 0.12, 0.05])
            sev = np.random.choice(SEVERIDADES, p=[0.50, 0.30, 0.15, 0.05])

        inst_row = instalaciones_df[instalaciones_df['instalacion_id'] == inst_id].iloc[0]
        fecha_base = pd.to_datetime(inst_row['fecha_instalacion'], errors='coerce')
        if pd.isna(fecha_base): fecha_base = pd.to_datetime('2020-06-01')

        dias_rango = max((pd.to_datetime('2021-03-31') - fecha_base).days, 1)
        if dias_rango < 0:
            dias_rango = 365
            fecha_base = pd.to_datetime('2020-01-01')

        timestamp = fecha_base + pd.Timedelta(
            days=int(np.random.randint(0, dias_rango)), hours=int(np.random.randint(0, 24)),
            minutes=int(np.random.randint(0, 60)), seconds=int(np.random.randint(0, 60)))

        eventos.append({
            'evento_id': i, 'instalacion_id': inst_id, 'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'tipo_evento': tipo, 'severidad': sev, 'es_anomalo': es_anomalo
        })
    return pd.DataFrame(eventos)

def crear_graficos(eventos_df, reporte_df, instalaciones_df, versiones_df, clientes_df, anomalias_dict, ruta='visualizations/'):
    print(f"\n[ROL2] Generando 5 visualizaciones críticas basadas en los hallazgos...")

    # 1. ANOMALÍAS
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    anomalos_c = eventos_df['es_anomalo'].value_counts()
    axes[0].pie([anomalos_c.get(False, 0), anomalos_c.get(True, 0)], labels=['Normal', 'Anómalo'],
                colors=[COLORES['primario'], COLORES['critico']], explode=(0, 0.1), autopct='%1.1f%%', shadow=True)
    axes[0].set_title('Proporcion de Eventos')

    eventos_anom = eventos_df[eventos_df['es_anomalo'] == True]
    if len(eventos_anom) > 0:
        tipo_c = eventos_anom['tipo_evento'].value_counts()
        axes[1].barh(tipo_c.index, tipo_c.values, color=COLORES['critico'], alpha=0.8)
        axes[1].set_title('Tipos de Eventos Anomalos')
    plt.tight_layout()
    plt.savefig(ruta + 'anomalias.png', dpi=150)
    plt.close()

    # 2. SEVERIDAD
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sev_order = ['Baja', 'Media', 'Alta', 'Crítica']
    for idx, (val, label, ax) in enumerate([(False, 'Normales', axes[0]), (True, 'Anomalos', axes[1])]):
        subset = eventos_df[eventos_df['es_anomalo'] == val]
        if len(subset) > 0:
            sev_c = subset['severidad'].value_counts().reindex(sev_order, fill_value=0)
            ax.bar(sev_c.index, sev_c.values, color=['#34a853', '#fbbc04', '#ea4335', '#d93025'])
            ax.set_title(f'Severidad: {label}')
    plt.tight_layout()
    plt.savefig(ruta + 'severidad_eventos.png', dpi=150)
    plt.close()

    # 3. CLIENTES AFECTADOS
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    crit_c = clientes_df['criticidad'].value_counts().reindex(['Alta', 'Media', 'Baja'], fill_value=0)
    axes[0].bar(crit_c.index, crit_c.values, color=[COLORES['critico'], COLORES['alerta'], COLORES['exito']])
    axes[0].set_title('Criticidad Clientes Originales')
    
    sector_c = clientes_df['sector'].value_counts()
    axes[1].barh(sector_c.index, sector_c.values, color=sns.color_palette('Blues_d', len(sector_c)))
    axes[1].set_title('Distribucion por Sector')
    plt.tight_layout()
    plt.savefig(ruta + 'clientes_afectados.png', dpi=150)
    plt.close()

    # 4. CALIDAD DE DATOS HEATMAP
    fig, ax = plt.subplots(figsize=(14, 10))
    pivot_data = reporte_df.pivot_table(index=['tabla', 'columna'], columns='metrica', values='valor_actual', aggfunc='first')
    labels = [f"{t} | {c}" for t, c in pivot_data.index]
    sns.heatmap(pivot_data.values, xticklabels=pivot_data.columns, yticklabels=labels, annot=True, fmt='.1f', cmap='RdYlGn', vmin=85, vmax=100, ax=ax)
    ax.set_title('Metricas DAMA DMBOK - Analisis Critico')
    plt.tight_layout()
    plt.savefig(ruta + 'calidad_datos.png', dpi=150)
    plt.close()

    # 5. CASCADA
    fig, ax = plt.subplots(figsize=(12, 7))
    cascada = anomalias_dict.get('cascada', {})
    etapas = ['Descargas Caso Real', 'Versiones SUNBURST\n(Caso Real)', 'Instalaciones\nSimuladas', 'Con SUNBURST', 'Comprometidos', 'Clientes']
    valores = [18000, 18000, cascada.get('total_instalaciones', 100), cascada.get('con_sunburst', 78), cascada.get('comprometidos', 12), cascada.get('clientes_unicos', 10)]
    bars = ax.bar(range(len(etapas)), valores, color=['#1a73e8', '#4285f4', '#5f6368', '#ea4335', '#d93025', '#b71c1c'])
    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200, f'{val:,}', ha='center')
    ax.set_xticks(range(len(etapas)))
    ax.set_xticklabels(etapas, fontsize=10)
    ax.set_title('Cascada: De 18,000 Descargas a <100 Comprometidos')
    plt.tight_layout()
    plt.savefig(ruta + 'grafico_cascada.png', dpi=150)
    plt.close()
    
    print("    ✓ Gráficos avanzados restaurados y guardados en visualizations/")


if __name__ == '__main__':
    print("======================================================================")
    print("  ROL 2: ANÁLISIS DE CALIDAD - VALIDACIÓN CRÍTICA")
    print("======================================================================")
    
    clientes = pd.read_csv('data/clientes.csv')
    versiones = pd.read_csv('data/versiones_software.csv')
    instalaciones = pd.read_csv('data/instalaciones.csv')
    
    resultados = validar_datos(clientes, versiones, instalaciones)
    reporte = calcular_metricas_dama(clientes, versiones, instalaciones)
    eventos = generar_eventos_seguridad(instalaciones, versiones, n=200)
    anomalias = detectar_anomalias(instalaciones, eventos, versiones, clientes)
    
    crear_graficos(eventos, reporte, instalaciones, versiones, clientes, anomalias, ruta='visualizations/')
    
    eventos.to_csv('data/eventos_seguridad.csv', index=False)
    reporte.to_csv('data/reporte_calidad.csv', index=False)
    print("\n[ROL2] Ejecución completada. CSVs guardados. Gráficos listos.")
