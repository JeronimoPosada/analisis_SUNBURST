"""
=============================================================================
ROL 2: Analista de Calidad - Validación y Detección de Patrones
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

Este script valida la calidad de los datos generados por el Rol 1,
genera eventos de seguridad, detecta anomalías REALES y crea visualizaciones.

Los datos del Rol 1 contienen anomalías intencionales que este script
detecta y reporta de forma crítica.

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
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime, timedelta

# Configuración de reproducibilidad
np.random.seed(42)

# Estilo profesional para gráficos
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

COLORES = {
    'primario': '#1a73e8',
    'secundario': '#ea4335',
    'exito': '#34a853',
    'alerta': '#fbbc04',
    'critico': '#d93025',
    'neutro': '#5f6368',
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
    Validación exhaustiva de los datos. Detecta anomalías REALES:
    - Nulos en cualquier columna
    - IDs duplicados
    - FK huérfanas (integridad referencial rota)
    - Fechas fuera de rango o inconsistentes
    - Valores categóricos inválidos
    - Strings vacíos

    Retorna un diccionario detallado con cada hallazgo.
    """
    print("[ROL2] Validando datos (análisis crítico)...")
    resultados = {}
    problemas_criticos = 0
    problemas_advertencia = 0

    # ===== 1. VALORES NULOS =====
    print("\n    [1/6] Verificando valores nulos...")
    nulos_detalle = {}
    for nombre, df in [('clientes', clientes_df), ('versiones_software', versiones_df),
                        ('instalaciones', instalaciones_df)]:
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

    # ===== 2. STRINGS VACÍOS =====
    print("\n    [2/6] Verificando strings vacíos...")
    vacios_detalle = {}
    for nombre, df in [('clientes', clientes_df), ('versiones_software', versiones_df),
                        ('instalaciones', instalaciones_df)]:
        for col in df.select_dtypes(include='object').columns:
            vacios = (df[col].fillna('').str.strip() == '').sum() - df[col].isnull().sum()
            if vacios > 0:
                vacios_detalle[f'{nombre}.{col}'] = int(vacios)
                print(f"      ❌ {nombre}.{col}: {vacios} strings vacíos")
                problemas_advertencia += 1

    resultados['strings_vacios'] = vacios_detalle

    # ===== 3. IDs DUPLICADOS =====
    print("\n    [3/6] Verificando IDs duplicados...")
    for nombre, df, id_col in [('clientes', clientes_df, 'cliente_id'),
                                ('versiones_software', versiones_df, 'version_id'),
                                ('instalaciones', instalaciones_df, 'instalacion_id')]:
        dups = df[id_col].duplicated().sum()
        if dups > 0:
            ids_dup = df[df[id_col].duplicated(keep=False)][id_col].unique().tolist()
            print(f"      ❌ {nombre}.{id_col}: {dups} duplicados (IDs: {ids_dup})")
            problemas_criticos += 1
        else:
            print(f"      ✅ {nombre}.{id_col}: sin duplicados")

    resultados['duplicados'] = {
        'clientes': clientes_df['cliente_id'].duplicated().sum(),
        'versiones': versiones_df['version_id'].duplicated().sum(),
        'instalaciones': instalaciones_df['instalacion_id'].duplicated().sum()
    }

    # ===== 4. INTEGRIDAD REFERENCIAL =====
    print("\n    [4/6] Verificando integridad referencial...")
    clientes_ids = set(clientes_df['cliente_id'].tolist())
    versiones_ids = set(versiones_df['version_id'].tolist())

    fk_cli_inv = instalaciones_df[~instalaciones_df['cliente_id'].isin(clientes_ids)]
    fk_ver_inv = instalaciones_df[~instalaciones_df['version_id'].isin(versiones_ids)]

    if len(fk_cli_inv) > 0:
        ids_huerfanos = fk_cli_inv['cliente_id'].unique().tolist()
        print(f"      ❌ instalaciones.cliente_id: {len(fk_cli_inv)} FK huérfanas "
              f"(IDs inexistentes: {ids_huerfanos})")
        problemas_criticos += 1
    else:
        print(f"      ✅ instalaciones.cliente_id: integridad OK")

    if len(fk_ver_inv) > 0:
        ids_huerfanos = fk_ver_inv['version_id'].unique().tolist()
        print(f"      ❌ instalaciones.version_id: {len(fk_ver_inv)} FK huérfanas "
              f"(IDs inexistentes: {ids_huerfanos})")
        problemas_criticos += 1
    else:
        print(f"      ✅ instalaciones.version_id: integridad OK")

    resultados['integridad_referencial'] = {
        'fk_clientes_invalidos': len(fk_cli_inv),
        'fk_clientes_ids': fk_cli_inv['cliente_id'].unique().tolist() if len(fk_cli_inv) > 0 else [],
        'fk_versiones_invalidos': len(fk_ver_inv),
        'fk_versiones_ids': fk_ver_inv['version_id'].unique().tolist() if len(fk_ver_inv) > 0 else [],
    }

    # ===== 5. RANGOS DE FECHAS Y CONSISTENCIA TEMPORAL =====
    print("\n    [5/6] Verificando fechas y consistencia temporal...")

    # Fechas fuera de rango
    fechas_inst = pd.to_datetime(instalaciones_df['fecha_instalacion'], errors='coerce')
    fuera_rango = fechas_inst[(fechas_inst < FECHA_MIN) | (fechas_inst > FECHA_MAX)]
    if len(fuera_rango) > 0:
        print(f"      ❌ {len(fuera_rango)} fechas fuera del rango 2019-2021:")
        for idx in fuera_rango.index:
            print(f"         Fila {idx+1}: {instalaciones_df.loc[idx, 'fecha_instalacion']}")
        problemas_criticos += 1
    else:
        print(f"      ✅ Todas las fechas dentro del rango")

    # Consistencia temporal: instalación >= release
    versiones_con_fecha = versiones_df.dropna(subset=['fecha_release'])
    inst_merge = instalaciones_df.merge(
        versiones_con_fecha[['version_id', 'fecha_release']],
        on='version_id', how='left'
    )
    inst_merge['fecha_instalacion_dt'] = pd.to_datetime(inst_merge['fecha_instalacion'], errors='coerce')
    inst_merge['fecha_release_dt'] = pd.to_datetime(inst_merge['fecha_release'], errors='coerce')

    # Solo verificar donde ambas fechas son válidas
    mask_valida = inst_merge['fecha_release_dt'].notna() & inst_merge['fecha_instalacion_dt'].notna()
    inconsistentes = inst_merge[mask_valida & (inst_merge['fecha_instalacion_dt'] < inst_merge['fecha_release_dt'])]

    if len(inconsistentes) > 0:
        print(f"      ❌ {len(inconsistentes)} instalaciones con fecha ANTERIOR al release:")
        for _, row in inconsistentes.iterrows():
            print(f"         Instalación {int(row['instalacion_id'])}: "
                  f"instalado {row['fecha_instalacion']} < release {row['fecha_release']}")
        problemas_criticos += 1
    else:
        print(f"      ✅ Coherencia temporal OK")

    # Versiones sin fecha release
    ver_sin_fecha = versiones_df[versiones_df['fecha_release'].isnull()]
    if len(ver_sin_fecha) > 0:
        print(f"      ⚠️  {len(ver_sin_fecha)} versiones sin fecha_release:")
        for _, row in ver_sin_fecha.iterrows():
            print(f"         Versión {int(row['version_id'])}: {row['nombre_version']}")
        problemas_advertencia += 1

    resultados['fechas'] = {
        'fuera_rango': len(fuera_rango),
        'inconsistentes_temporales': len(inconsistentes),
        'versiones_sin_fecha': len(ver_sin_fecha)
    }

    # ===== 6. VALORES CATEGÓRICOS INVÁLIDOS =====
    print("\n    [6/6] Verificando valores categóricos...")
    cats_invalidas = {}

    for col, validos in [('tipo_org', TIPOS_ORG_VALIDOS), ('sector', SECTORES_VALIDOS),
                          ('criticidad', CRITICIDADES_VALIDAS)]:
        inv = clientes_df[clientes_df[col].notna() & ~clientes_df[col].isin(validos)]
        if len(inv) > 0:
            valores = inv[col].unique().tolist()
            cats_invalidas[f'clientes.{col}'] = {'cantidad': len(inv), 'valores': valores}
            print(f"      ❌ clientes.{col}: {len(inv)} valores inválidos: {valores}")
            problemas_advertencia += 1
        else:
            print(f"      ✅ clientes.{col}: valores válidos")

    # nivel_datos_sensibles en instalaciones
    inv_nivel = instalaciones_df[
        instalaciones_df['nivel_datos_sensibles'].notna() &
        ~instalaciones_df['nivel_datos_sensibles'].isin(NIVELES_SENSIBLES_VALIDOS)
    ]
    if len(inv_nivel) > 0:
        valores = inv_nivel['nivel_datos_sensibles'].unique().tolist()
        cats_invalidas['instalaciones.nivel_datos_sensibles'] = {'cantidad': len(inv_nivel), 'valores': valores}
        print(f"      ❌ instalaciones.nivel_datos_sensibles: {len(inv_nivel)} valores inválidos: {valores}")
        problemas_advertencia += 1
    else:
        print(f"      ✅ instalaciones.nivel_datos_sensibles: valores válidos")

    resultados['categorias_invalidas'] = cats_invalidas

    # ===== RESUMEN =====
    print(f"\n    {'=' * 50}")
    print(f"    RESUMEN DE VALIDACIÓN:")
    print(f"    🔴 Problemas CRÍTICOS: {problemas_criticos}")
    print(f"    🟡 Advertencias: {problemas_advertencia}")
    print(f"    {'=' * 50}")
    resultados['resumen'] = {
        'problemas_criticos': problemas_criticos,
        'problemas_advertencia': problemas_advertencia
    }

    return resultados


def calcular_metricas_dama(clientes_df, versiones_df, instalaciones_df):
    """
    Calcula métricas DAMA DMBOK con evaluación crítica.
    Las métricas reflejan los problemas REALES encontrados en los datos.
    """
    print("\n[ROL2] Calculando métricas DAMA DMBOK (análisis crítico)...")
    reportes = []

    dataframes = {
        'clientes': clientes_df,
        'versiones_software': versiones_df,
        'instalaciones': instalaciones_df
    }

    for nombre_tabla, df in dataframes.items():
        print(f"    → Evaluando tabla: {nombre_tabla}")

        for columna in df.columns:
            total = len(df)

            # --- COMPLETITUD ---
            no_nulos = df[columna].notna().sum()

            # Contar strings vacíos como "incompletos"
            if df[columna].dtype == 'object':
                vacios = df[columna].fillna('').apply(lambda x: str(x).strip() == '').sum()
                completitud_real = round(((total - vacios) / total) * 100, 2)
            else:
                completitud_real = round((no_nulos / total) * 100, 2)

            umbral_comp = 95.0
            estado_comp = 'APROBADO' if completitud_real >= umbral_comp else 'FALLIDO'

            reportes.append({
                'tabla': nombre_tabla, 'columna': columna, 'metrica': 'Completitud',
                'valor_actual': completitud_real, 'umbral': umbral_comp, 'estado': estado_comp
            })

            # --- EXACTITUD ---
            if df[columna].dtype == 'object':
                # Verificar contra valores válidos conocidos
                if columna == 'tipo_org':
                    validos = df[columna].isin(TIPOS_ORG_VALIDOS) | df[columna].isna()
                    exactitud = round((validos.sum() / total) * 100, 2)
                elif columna == 'sector':
                    validos = df[columna].isin(SECTORES_VALIDOS) | df[columna].isna()
                    exactitud = round((validos.sum() / total) * 100, 2)
                elif columna == 'criticidad':
                    validos = df[columna].isin(CRITICIDADES_VALIDAS) | df[columna].isna()
                    exactitud = round((validos.sum() / total) * 100, 2)
                elif columna == 'nivel_datos_sensibles':
                    validos = df[columna].isin(NIVELES_SENSIBLES_VALIDOS) | df[columna].isna()
                    exactitud = round((validos.sum() / total) * 100, 2)
                elif columna == 'pais':
                    # País vacío = inexacto
                    no_vacios = df[columna].fillna('').apply(lambda x: len(str(x).strip()) > 0).sum()
                    exactitud = round((no_vacios / total) * 100, 2)
                else:
                    vacios = df[columna].fillna('').apply(lambda x: str(x).strip() == '').sum()
                    exactitud = round(((total - vacios) / total) * 100, 2)
            elif pd.api.types.is_numeric_dtype(df[columna]):
                if '_id' in columna:
                    positivos = (df[columna] > 0).sum()
                    exactitud = round((positivos / total) * 100, 2)
                else:
                    exactitud = 100.0
            elif pd.api.types.is_bool_dtype(df[columna]):
                exactitud = 100.0
            else:
                # Fechas: verificar que no son nulas
                exactitud = round((df[columna].notna().sum() / total) * 100, 2)

            umbral_exact = 90.0
            estado_exact = 'APROBADO' if exactitud >= umbral_exact else 'FALLIDO'

            reportes.append({
                'tabla': nombre_tabla, 'columna': columna, 'metrica': 'Exactitud',
                'valor_actual': exactitud, 'umbral': umbral_exact, 'estado': estado_exact
            })

    # --- CONSISTENCIA ---
    print("    → Evaluando consistencia entre tablas...")

    # FK cliente_id
    clientes_ids = set(clientes_df['cliente_id'].tolist())
    fk_cli_val = instalaciones_df['cliente_id'].isin(clientes_ids).sum()
    consist_cli = round((fk_cli_val / len(instalaciones_df)) * 100, 2)
    reportes.append({
        'tabla': 'instalaciones', 'columna': 'cliente_id (FK→clientes)',
        'metrica': 'Consistencia', 'valor_actual': consist_cli,
        'umbral': 100.0, 'estado': 'APROBADO' if consist_cli == 100.0 else 'FALLIDO'
    })

    # FK version_id
    versiones_ids = set(versiones_df['version_id'].tolist())
    fk_ver_val = instalaciones_df['version_id'].isin(versiones_ids).sum()
    consist_ver = round((fk_ver_val / len(instalaciones_df)) * 100, 2)
    reportes.append({
        'tabla': 'instalaciones', 'columna': 'version_id (FK→versiones)',
        'metrica': 'Consistencia', 'valor_actual': consist_ver,
        'umbral': 100.0, 'estado': 'APROBADO' if consist_ver == 100.0 else 'FALLIDO'
    })

    # Coherencia temporal
    versiones_con_fecha = versiones_df.dropna(subset=['fecha_release'])
    inst_merge = instalaciones_df.merge(
        versiones_con_fecha[['version_id', 'fecha_release']],
        on='version_id', how='inner'
    )
    if len(inst_merge) > 0:
        fechas_inst = pd.to_datetime(inst_merge['fecha_instalacion'], errors='coerce')
        fechas_rel = pd.to_datetime(inst_merge['fecha_release'], errors='coerce')
        mask = fechas_inst.notna() & fechas_rel.notna()
        coherentes = (fechas_inst[mask] >= fechas_rel[mask]).sum()
        total_comparables = mask.sum()
        consist_fecha = round((coherentes / total_comparables) * 100, 2) if total_comparables > 0 else 0.0
    else:
        consist_fecha = 0.0

    reportes.append({
        'tabla': 'instalaciones', 'columna': 'fecha_instalacion >= fecha_release',
        'metrica': 'Consistencia', 'valor_actual': consist_fecha,
        'umbral': 100.0, 'estado': 'APROBADO' if consist_fecha == 100.0 else 'FALLIDO'
    })

    # Rango temporal
    fechas_all = pd.to_datetime(instalaciones_df['fecha_instalacion'], errors='coerce')
    en_rango = ((fechas_all >= FECHA_MIN) & (fechas_all <= FECHA_MAX)).sum()
    consist_rango = round((en_rango / len(instalaciones_df)) * 100, 2)
    reportes.append({
        'tabla': 'instalaciones', 'columna': 'fecha_instalacion (rango 2019-2021)',
        'metrica': 'Consistencia', 'valor_actual': consist_rango,
        'umbral': 100.0, 'estado': 'APROBADO' if consist_rango == 100.0 else 'FALLIDO'
    })

    # Unicidad de PKs
    for nombre, df, pk in [('clientes', clientes_df, 'cliente_id'),
                            ('versiones_software', versiones_df, 'version_id'),
                            ('instalaciones', instalaciones_df, 'instalacion_id')]:
        unicos = df[pk].nunique()
        consist_pk = round((unicos / len(df)) * 100, 2)
        reportes.append({
            'tabla': nombre, 'columna': f'{pk} (unicidad PK)',
            'metrica': 'Consistencia', 'valor_actual': consist_pk,
            'umbral': 100.0, 'estado': 'APROBADO' if consist_pk == 100.0 else 'FALLIDO'
        })

    reporte_df = pd.DataFrame(reportes)

    # Resumen crítico
    aprobados = (reporte_df['estado'] == 'APROBADO').sum()
    fallidos = (reporte_df['estado'] == 'FALLIDO').sum()
    total_metricas = len(reporte_df)
    tasa = round(aprobados / total_metricas * 100, 1)

    print(f"\n    {'=' * 50}")
    print(f"    RESULTADOS DAMA DMBOK:")
    print(f"    Total métricas: {total_metricas}")
    print(f"    ✅ APROBADAS: {aprobados} ({tasa}%)")
    print(f"    ❌ FALLIDAS: {fallidos} ({round(100-tasa,1)}%)")

    # Detallar las fallidas
    fallidas = reporte_df[reporte_df['estado'] == 'FALLIDO']
    if len(fallidas) > 0:
        print(f"\n    Métricas FALLIDAS:")
        for _, row in fallidas.iterrows():
            print(f"      → {row['tabla']}.{row['columna']} [{row['metrica']}]: "
                  f"{row['valor_actual']}% (umbral: {row['umbral']}%)")

    print(f"    {'=' * 50}")

    return reporte_df


def detectar_anomalias(instalaciones_df, eventos_df, versiones_df, clientes_df):
    """
    Detección crítica de anomalías con análisis estadístico y contextual.
    """
    print("\n[ROL2] Detectando anomalías (análisis crítico)...")
    anomalias = {}

    # 1. Concentración temporal de instalaciones
    print("    → Analizando distribución temporal de instalaciones...")
    fechas = pd.to_datetime(instalaciones_df['fecha_instalacion'], errors='coerce')
    fechas_validas = fechas.dropna()
    if len(fechas_validas) > 0:
        por_mes = fechas_validas.dt.to_period('M').value_counts().sort_index()
        mes_pico = por_mes.idxmax()
        print(f"      Mes con más instalaciones: {mes_pico} ({por_mes.max()} instalaciones)")

    # 2. Análisis de eventos anómalos
    print("    → Analizando eventos de seguridad...")
    eventos_anomalos = eventos_df[eventos_df['es_anomalo'] == True]
    anomalias['eventos'] = {
        'total': len(eventos_df),
        'anomalos': len(eventos_anomalos),
        'porcentaje': round(len(eventos_anomalos) / len(eventos_df) * 100, 2),
        'tipos_anomalos': eventos_anomalos['tipo_evento'].value_counts().to_dict(),
        'severidad_anomalos': eventos_anomalos['severidad'].value_counts().to_dict()
    }
    print(f"      Eventos anómalos: {len(eventos_anomalos)}/{len(eventos_df)} "
          f"({anomalias['eventos']['porcentaje']}%)")

    # 3. Cascada 18,000 → <100
    print("    → Simulando cascada de filtrado 18,000 → <100...")
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()

    inst_afectadas = instalaciones_df[instalaciones_df['version_id'].isin(versiones_sunburst)]
    ids_con_eventos = set(eventos_df['instalacion_id'].tolist())
    con_eventos = inst_afectadas[inst_afectadas['instalacion_id'].isin(ids_con_eventos)]
    ids_anomalos = set(eventos_anomalos['instalacion_id'].tolist())
    comprometidos = inst_afectadas[inst_afectadas['instalacion_id'].isin(ids_anomalos)]

    # Filtrar FK huérfanas para clientes comprometidos
    clientes_ids_validos = set(clientes_df['cliente_id'].tolist())
    comprometidos_validos = comprometidos[comprometidos['cliente_id'].isin(clientes_ids_validos)]
    clientes_comp = comprometidos_validos['cliente_id'].nunique()

    anomalias['cascada'] = {
        'total_instalaciones': len(instalaciones_df),
        'con_sunburst': len(inst_afectadas),
        'con_eventos': len(con_eventos),
        'comprometidos': len(comprometidos),
        'clientes_unicos': clientes_comp
    }

    print(f"      Total: {len(instalaciones_df)} → SUNBURST: {len(inst_afectadas)} "
          f"→ Comprometidos: {len(comprometidos)} → Clientes: {clientes_comp}")

    # 4. Análisis de criticidad de comprometidos
    if len(comprometidos_validos) > 0:
        comprometidos_con_info = comprometidos_validos.merge(
            clientes_df[['cliente_id', 'tipo_org', 'sector', 'criticidad']].drop_duplicates(),
            on='cliente_id', how='left'
        )
        print(f"\n    → Perfil de clientes comprometidos:")
        if 'criticidad' in comprometidos_con_info.columns:
            crit_dist = comprometidos_con_info['criticidad'].value_counts()
            for crit, count in crit_dist.items():
                print(f"      {crit}: {count} instalaciones")

    print("    ✓ Análisis de anomalías completado")
    return anomalias


def generar_eventos_seguridad(instalaciones_df, versiones_df, n=200):
    """
    Genera eventos de seguridad con distribución realista:
    - ~80% en instalaciones SUNBURST
    - ~5-7% de eventos anómalos
    - Eventos anómalos concentrados en tipos severos
    """
    print(f"\n[ROL2] Generando {n} eventos de seguridad...")

    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    inst_sunburst = instalaciones_df[
        instalaciones_df['version_id'].isin(versiones_sunburst)
    ]['instalacion_id'].tolist()

    inst_limpias = instalaciones_df[
        ~instalaciones_df['version_id'].isin(versiones_sunburst)
    ]['instalacion_id'].tolist()

    # Manejar caso donde no hay instalaciones limpias
    if len(inst_limpias) == 0:
        inst_limpias = inst_sunburst

    eventos = []
    for i in range(1, n + 1):
        if np.random.random() < 0.80 and len(inst_sunburst) > 0:
            inst_id = np.random.choice(inst_sunburst)
        else:
            inst_id = np.random.choice(inst_limpias)

        es_anomalo = False
        if inst_id in inst_sunburst and np.random.random() < 0.065:
            es_anomalo = True

        if es_anomalo:
            tipo = np.random.choice(
                ['conexion_c2', 'exfiltracion', 'escalamiento_privilegios',
                 'movimiento_lateral', 'modificacion_logs'],
                p=[0.30, 0.25, 0.20, 0.15, 0.10])
            sev = np.random.choice(SEVERIDADES, p=[0.05, 0.10, 0.40, 0.45])
        else:
            tipo = np.random.choice(TIPOS_EVENTO,
                                    p=[0.35, 0.15, 0.05, 0.02, 0.01, 0.15, 0.05, 0.05, 0.12, 0.05])
            sev = np.random.choice(SEVERIDADES, p=[0.50, 0.30, 0.15, 0.05])

        inst_row = instalaciones_df[instalaciones_df['instalacion_id'] == inst_id].iloc[0]
        fecha_base = pd.to_datetime(inst_row['fecha_instalacion'], errors='coerce')
        if pd.isna(fecha_base):
            fecha_base = datetime(2020, 6, 1)

        fecha_fin = datetime(2021, 3, 31)
        dias_rango = max((fecha_fin - fecha_base).days, 1)
        if dias_rango < 0:
            dias_rango = 365  # Fallback para fechas inconsistentes
            fecha_base = datetime(2020, 1, 1)

        offset = np.random.randint(0, dias_rango)
        timestamp = fecha_base + timedelta(
            days=int(offset), hours=int(np.random.randint(0, 24)),
            minutes=int(np.random.randint(0, 60)), seconds=int(np.random.randint(0, 60)))

        eventos.append({
            'evento_id': i, 'instalacion_id': inst_id,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'tipo_evento': tipo, 'severidad': sev, 'es_anomalo': es_anomalo
        })

    df = pd.DataFrame(eventos)
    anomalos = df['es_anomalo'].sum()
    print(f"    ✓ {len(df)} eventos generados ({anomalos} anómalos, "
          f"{round(anomalos/len(df)*100, 1)}%)")
    return df


def crear_graficos(eventos_df, reporte_df, instalaciones_df, versiones_df, clientes_df,
                   anomalias_dict, ruta='../visualizations/'):
    """
    Genera 5 visualizaciones con análisis crítico de los datos.
    """
    os.makedirs(ruta, exist_ok=True)
    print(f"\n[ROL2] Generando visualizaciones críticas...")

    # =========================================================
    # 1. ANOMALÍAS
    # =========================================================
    print("    → 1/5: anomalias.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    anomalos_c = eventos_df['es_anomalo'].value_counts()
    axes[0].pie(
        [anomalos_c.get(False, 0), anomalos_c.get(True, 0)],
        labels=['Normal', 'Anómalo'],
        colors=[COLORES['primario'], COLORES['critico']],
        explode=(0, 0.1), autopct='%1.1f%%', shadow=True, startangle=90,
        textprops={'fontsize': 12, 'fontweight': 'bold'})
    axes[0].set_title('Proporcion de Eventos\nAnomalos vs Normales', fontweight='bold')

    eventos_anom = eventos_df[eventos_df['es_anomalo'] == True]
    if len(eventos_anom) > 0:
        tipo_c = eventos_anom['tipo_evento'].value_counts()
        barras = axes[1].barh(tipo_c.index, tipo_c.values, color=COLORES['critico'], alpha=0.8)
        axes[1].set_xlabel('Cantidad de Eventos')
        axes[1].set_title('Tipos de Eventos Anomalos', fontweight='bold')
        for b in barras:
            w = b.get_width()
            axes[1].text(w + 0.1, b.get_y() + b.get_height()/2,
                        f'{int(w)}', ha='left', va='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'anomalias.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # 2. SEVERIDAD
    # =========================================================
    print("    → 2/5: severidad_eventos.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    sev_order = ['Baja', 'Media', 'Alta', 'Critica']
    colores_sev = ['#34a853', '#fbbc04', '#ea4335', '#d93025']

    for idx, (val, label, ax) in enumerate([
        (False, 'Eventos Normales', axes[0]),
        (True, 'Eventos Anomalos', axes[1])
    ]):
        subset = eventos_df[eventos_df['es_anomalo'] == val]
        if len(subset) > 0:
            sev_c = subset['severidad'].value_counts().reindex(sev_order, fill_value=0)
            bars = ax.bar(sev_c.index, sev_c.values, color=colores_sev,
                         edgecolor='white', linewidth=1.5)
            ax.set_title(f'Severidad: {label}', fontweight='bold')
            ax.set_ylabel('Cantidad')
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, h + 0.5,
                           f'{int(h)}', ha='center', va='bottom', fontweight='bold')

    plt.suptitle('Distribucion de Severidad de Eventos de Seguridad',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'severidad_eventos.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # 3. CLIENTES AFECTADOS
    # =========================================================
    print("    → 3/5: clientes_afectados.png")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    crit_c = clientes_df['criticidad'].value_counts().reindex(['Alta', 'Media', 'Baja'], fill_value=0)
    nulos_crit = clientes_df['criticidad'].isnull().sum()
    colors_crit = [COLORES['critico'], COLORES['alerta'], COLORES['exito']]

    labels_crit = list(crit_c.index)
    vals_crit = list(crit_c.values)
    cols_crit = list(colors_crit)
    if nulos_crit > 0:
        labels_crit.append(f'NULL ({nulos_crit})')
        vals_crit.append(nulos_crit)
        cols_crit.append('#999999')

    bars = axes[0].bar(labels_crit, vals_crit, color=cols_crit,
                       edgecolor='white', linewidth=1.5)
    axes[0].set_title('Clientes por Nivel de Criticidad', fontweight='bold')
    axes[0].set_ylabel('Cantidad de Clientes')
    for bar in bars:
        h = bar.get_height()
        axes[0].text(bar.get_x() + bar.get_width()/2, h + 0.3,
                    f'{int(h)}', ha='center', va='bottom', fontweight='bold', fontsize=13)

    sector_c = clientes_df['sector'].value_counts()
    axes[1].barh(sector_c.index, sector_c.values,
                 color=sns.color_palette('Blues_d', len(sector_c)))
    axes[1].set_xlabel('Cantidad de Clientes')
    axes[1].set_title('Distribucion por Sector', fontweight='bold')
    for i, (v, n) in enumerate(zip(sector_c.values, sector_c.index)):
        axes[1].text(v + 0.2, i, f'{v}', ha='left', va='center', fontweight='bold')

    plt.suptitle('Analisis de Clientes Afectados por SUNBURST',
                 fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'clientes_afectados.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # 4. CALIDAD DE DATOS (heatmap con problemas visibles)
    # =========================================================
    print("    → 4/5: calidad_datos.png")
    fig, ax = plt.subplots(figsize=(14, 10))

    pivot_data = reporte_df.pivot_table(
        index=['tabla', 'columna'], columns='metrica',
        values='valor_actual', aggfunc='first'
    )
    labels = [f"{t} | {c}" for t, c in pivot_data.index]

    # Colormap que resalta problemas (rojo = malo, verde = bueno)
    sns.heatmap(
        pivot_data.values, xticklabels=pivot_data.columns, yticklabels=labels,
        annot=True, fmt='.1f', cmap='RdYlGn', vmin=85, vmax=100,
        linewidths=0.5, linecolor='white',
        cbar_kws={'label': 'Porcentaje (%)'},
        ax=ax
    )
    ax.set_title('Metricas de Calidad de Datos (DAMA DMBOK)\n'
                 'Completitud, Exactitud y Consistencia — Analisis Critico',
                 fontweight='bold', fontsize=14)
    ax.set_ylabel('')

    # Marcar las métricas fallidas
    fallidas = reporte_df[reporte_df['estado'] == 'FALLIDO']
    n_fallidas = len(fallidas)
    ax.text(0.5, -0.08, f'ADVERTENCIA: {n_fallidas} metricas FALLIDAS detectadas',
            transform=ax.transAxes, ha='center', fontsize=12,
            color=COLORES['critico'], fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'calidad_datos.png'), dpi=150, bbox_inches='tight')
    plt.close()

    # =========================================================
    # 5. CASCADA
    # =========================================================
    print("    → 5/5: grafico_cascada.png")
    fig, ax = plt.subplots(figsize=(12, 7))

    cascada = anomalias_dict.get('cascada', {})
    etapas = [
        'Total Descargas\nActivadas\n(Caso Real)',
        'Versiones con\nSUNBURST\n(Caso Real)',
        'Instalaciones\nSimuladas',
        'Con Versiones\nSUNBURST',
        'Realmente\nComprometidos',
        'Clientes Unicos\nComprometidos'
    ]
    valores = [
        18000, 18000,
        cascada.get('total_instalaciones', 100),
        cascada.get('con_sunburst', 78),
        cascada.get('comprometidos', 12),
        cascada.get('clientes_unicos', 10)
    ]

    colores_casc = ['#1a73e8', '#4285f4', '#5f6368', '#ea4335', '#d93025', '#b71c1c']
    bars = ax.bar(range(len(etapas)), valores, color=colores_casc,
                  edgecolor='white', linewidth=2, width=0.6)

    for bar, val in zip(bars, valores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
                f'{val:,}', ha='center', va='bottom', fontweight='bold', fontsize=13, color='#333')

    ax.set_xticks(range(len(etapas)))
    ax.set_xticklabels(etapas, fontsize=9)
    ax.set_ylabel('Numero de Instalaciones / Clientes', fontsize=12)
    ax.set_title('Grafico de Cascada: De 18,000 Descargas a <100 Comprometidos\n'
                 'Filtrado Progresivo del Incidente SUNBURST',
                 fontweight='bold', fontsize=14)

    ax.axvline(x=1.5, color='gray', linestyle='--', alpha=0.5)
    ax.text(0.5, max(valores) * 0.9, 'Caso Real', ha='center',
            fontsize=10, style='italic', color='gray')
    ax.text(3.5, max(valores) * 0.9, 'Datos Sinteticos', ha='center',
            fontsize=10, style='italic', color='gray')

    for i in range(len(valores) - 1):
        if valores[i] > valores[i+1]:
            reduccion = round((1 - valores[i+1]/valores[i]) * 100, 1)
            mid_y = (valores[i] + valores[i+1]) / 2
            ax.annotate(f'-{reduccion}%', xy=(i + 0.5, mid_y),
                       fontsize=9, color=COLORES['critico'], fontweight='bold', ha='center')

    ax.set_ylim(0, max(valores) * 1.15)
    plt.tight_layout()
    plt.savefig(os.path.join(ruta, 'grafico_cascada.png'), dpi=150, bbox_inches='tight')
    plt.close()

    print("    ✓ 5 graficos generados")


def guardar_csvs_rol2(eventos_df, reporte_df, ruta='../data/'):
    """Guarda CSVs del Rol 2."""
    os.makedirs(ruta, exist_ok=True)
    archivos = {'eventos_seguridad.csv': eventos_df, 'reporte_calidad.csv': reporte_df}

    print("\n[ROL2] Guardando archivos CSV...")
    for nombre, df in archivos.items():
        filepath = os.path.join(ruta, nombre)
        df.to_csv(filepath, index=False, encoding='utf-8')
        print(f"    ✓ {nombre} ({len(df)} registros) → {filepath}")


# ===========================================================================
# EJECUCIÓN PRINCIPAL
# ===========================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("  ROL 2: ANÁLISIS CRÍTICO DE CALIDAD DE DATOS - CASO SUNBURST")
    print("=" * 70)
    print()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    vis_dir = os.path.join(script_dir, '..', 'visualizations')

    # 1. Cargar datos
    print("[ROL2] Cargando datos del Rol 1...")
    clientes = pd.read_csv(os.path.join(data_dir, 'clientes.csv'))
    versiones = pd.read_csv(os.path.join(data_dir, 'versiones_software.csv'))
    instalaciones = pd.read_csv(os.path.join(data_dir, 'instalaciones.csv'))
    print(f"    Cargados: {len(clientes)} clientes, {len(versiones)} versiones, "
          f"{len(instalaciones)} instalaciones")

    # 2. Validación exhaustiva
    resultados = validar_datos(clientes, versiones, instalaciones)

    # 3. Métricas DAMA críticas
    reporte = calcular_metricas_dama(clientes, versiones, instalaciones)

    # 4. Generar eventos
    eventos = generar_eventos_seguridad(instalaciones, versiones, n=200)

    # 5. Anomalías
    anomalias = detectar_anomalias(instalaciones, eventos, versiones, clientes)

    # 6. Gráficos
    crear_graficos(eventos, reporte, instalaciones, versiones, clientes, anomalias, ruta=vis_dir)

    # 7. Guardar
    guardar_csvs_rol2(eventos, reporte, ruta=data_dir)

    # 8. Resumen final CRÍTICO
    print()
    print("=" * 70)
    print("  RESUMEN FINAL - ANÁLISIS CRÍTICO ROL 2")
    print("=" * 70)

    aprobadas = (reporte['estado'] == 'APROBADO').sum()
    fallidas = (reporte['estado'] == 'FALLIDO').sum()
    total = len(reporte)
    tasa = round(aprobadas / total * 100, 1)

    print(f"\n  MÉTRICAS DAMA DMBOK:")
    print(f"    Total evaluadas: {total}")
    print(f"    ✅ APROBADAS: {aprobadas} ({tasa}%)")
    print(f"    ❌ FALLIDAS:  {fallidas} ({round(100-tasa,1)}%)")

    print(f"\n  PROBLEMAS DE CALIDAD DETECTADOS:")
    print(f"    🔴 Críticos: {resultados['resumen']['problemas_criticos']}")
    print(f"    🟡 Advertencias: {resultados['resumen']['problemas_advertencia']}")

    print(f"\n  EVENTOS DE SEGURIDAD:")
    print(f"    Total: {len(eventos)}")
    print(f"    Anómalos: {eventos['es_anomalo'].sum()} ({round(eventos['es_anomalo'].mean()*100,1)}%)")

    cascada = anomalias['cascada']
    print(f"\n  CASCADA DE FILTRADO:")
    print(f"    {cascada['total_instalaciones']} → {cascada['con_sunburst']} → "
          f"{cascada['comprometidos']} → {cascada['clientes_unicos']} clientes")

    print("\n" + "=" * 70)
    print("  [ROL2] ¡Análisis crítico completado!")
    print("=" * 70)
