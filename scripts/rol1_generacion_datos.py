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

Uso:
    python rol1_generacion_datos.py
=============================================================================
"""

import pandas as pd
import numpy as np
from faker import Faker
import os
from datetime import datetime, timedelta

# Configuración de reproducibilidad
np.random.seed(42)
fake = Faker('es_ES')  # Faker en español
Faker.seed(42)

# ===========================================================================
# CONSTANTES Y DATOS BASE DEL CASO SUNBURST
# ===========================================================================

# Tipos de organización (basados en los clientes reales de SolarWinds)
TIPOS_ORGANIZACION = [
    'Gobierno Federal', 'Gobierno Estatal', 'Empresa Privada',
    'Institución Educativa', 'Organización de Salud', 'ONG'
]

# Sectores afectados según el caso (Cisco, Intel, Microsoft, agencias gubernamentales)
SECTORES = [
    'Tecnología', 'Defensa', 'Energía', 'Finanzas',
    'Telecomunicaciones', 'Salud', 'Gobierno', 'Educación'
]

# Niveles de criticidad
CRITICIDADES = ['Alta', 'Media', 'Baja']

# Niveles de datos sensibles
NIVELES_DATOS_SENSIBLES = ['Bajo', 'Medio', 'Alto', 'Crítico']

# Países (principalmente EE.UU., como en el caso real)
PAISES = [
    'Estados Unidos', 'Estados Unidos', 'Estados Unidos', 'Estados Unidos',
    'Estados Unidos', 'Estados Unidos', 'Estados Unidos',  # 70% EE.UU.
    'Reino Unido', 'Canadá', 'Alemania', 'Israel',
    'Australia', 'Francia', 'Japón'
]


def generar_clientes(n=50):
    """
    Genera un DataFrame de clientes que simulan organizaciones que usaban
    la Plataforma Orion de SolarWinds.

    Parámetros:
        n (int): Número de clientes a generar. Por defecto 50.

    Retorna:
        pd.DataFrame: DataFrame con columnas:
            - cliente_id (int): Identificador único del cliente (1 a n)
            - nombre_organizacion (str): Nombre ficticio de la organización
            - tipo_org (str): Tipo de organización
            - pais (str): País de la organización
            - sector (str): Sector de la industria
            - criticidad (str): Nivel de criticidad (Alta, Media, Baja)
    """
    print(f"[ROL1] Generando {n} clientes...")

    # Nombres de organizaciones realistas (mezcla de empresas y gobierno)
    nombres_base = [
        'TechCorp', 'DataSystems', 'InfoSec Solutions', 'CyberNet',
        'GlobalTech', 'SecureData', 'NetWatch', 'CloudBase',
        'SysTech', 'TechVault', 'Departamento de', 'Ministerio de',
        'Agencia de', 'Instituto', 'Corporación', 'Fundación'
    ]

    clientes = []
    for i in range(1, n + 1):
        tipo_org = np.random.choice(TIPOS_ORGANIZACION, p=[0.15, 0.10, 0.40, 0.10, 0.15, 0.10])

        # Generar nombre según tipo de organización
        if 'Gobierno' in tipo_org:
            nombre = f"{np.random.choice(['Departamento de', 'Agencia de', 'Ministerio de'])} {fake.word().capitalize()} {fake.word().capitalize()}"
        elif tipo_org == 'Institución Educativa':
            nombre = f"Universidad {fake.city()}"
        elif tipo_org == 'Organización de Salud':
            nombre = f"Hospital {fake.last_name()} {fake.city()}"
        else:
            nombre = f"{fake.company()}"

        # Criticidad: organizaciones gubernamentales/defensa tienden a ser más críticas
        if 'Gobierno' in tipo_org:
            criticidad = np.random.choice(CRITICIDADES, p=[0.6, 0.3, 0.1])
            sector = np.random.choice(['Gobierno', 'Defensa', 'Energía'])
        elif tipo_org == 'Organización de Salud':
            criticidad = np.random.choice(CRITICIDADES, p=[0.5, 0.35, 0.15])
            sector = 'Salud'
        else:
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
    print(f"    ✓ {len(df)} clientes generados correctamente")
    return df


def generar_versiones():
    """
    Genera un DataFrame con las versiones de la Plataforma Orion de SolarWinds.
    Las versiones están basadas en la información real del caso SUNBURST:
    - Versiones 2019.4 (antes de HF5) contenían SUNBURST
    - Versión 2020.2 y 2020.2 HF1 contenían SUNBURST
    - Versión 2019.4 HF5 y 2020.2.1 eran los parches limpios

    Retorna:
        pd.DataFrame: DataFrame con columnas:
            - version_id (int): Identificador único de la versión
            - nombre_version (str): Nombre de la versión
            - fecha_release (datetime): Fecha de lanzamiento
            - contiene_sunburst (bool): Si contiene el malware SUNBURST
            - fecha_compilacion (datetime): Fecha de compilación del software
    """
    print("[ROL1] Generando versiones de software...")

    versiones = [
        {
            'version_id': 1,
            'nombre_version': 'Orion Platform 2019.4',
            'fecha_release': datetime(2019, 10, 22),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2019, 10, 10)
        },
        {
            'version_id': 2,
            'nombre_version': 'Orion Platform 2019.4 HF1',
            'fecha_release': datetime(2019, 12, 17),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2019, 12, 5)
        },
        {
            'version_id': 3,
            'nombre_version': 'Orion Platform 2019.4 HF2',
            'fecha_release': datetime(2020, 1, 23),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2020, 1, 10)
        },
        {
            'version_id': 4,
            'nombre_version': 'Orion Platform 2019.4 HF3',
            'fecha_release': datetime(2020, 3, 5),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2020, 2, 20)  # Fecha clave: SUNBURST compilado ~20/Feb/2020
        },
        {
            'version_id': 5,
            'nombre_version': 'Orion Platform 2019.4 HF5',
            'fecha_release': datetime(2020, 3, 26),
            'contiene_sunburst': False,  # Parche limpio
            'fecha_compilacion': datetime(2020, 3, 15)
        },
        {
            'version_id': 6,
            'nombre_version': 'Orion Platform 2020.2',
            'fecha_release': datetime(2020, 6, 19),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2020, 6, 4)
        },
        {
            'version_id': 7,
            'nombre_version': 'Orion Platform 2020.2 HF1',
            'fecha_release': datetime(2020, 9, 14),
            'contiene_sunburst': True,
            'fecha_compilacion': datetime(2020, 9, 1)
        },
        {
            'version_id': 8,
            'nombre_version': 'Orion Platform 2020.2.1',
            'fecha_release': datetime(2020, 12, 15),
            'contiene_sunburst': False,  # Parche de remediación post-descubrimiento
            'fecha_compilacion': datetime(2020, 12, 14)
        },
    ]

    df = pd.DataFrame(versiones)
    print(f"    ✓ {len(df)} versiones generadas ({df['contiene_sunburst'].sum()} con SUNBURST)")
    return df


def generar_instalaciones(clientes_df, versiones_df, n=100):
    """
    Genera un DataFrame de instalaciones que relaciona clientes con versiones
    del software. Simula el escenario real donde ~18,000 organizaciones
    descargaron versiones afectadas.

    Parámetros:
        clientes_df (pd.DataFrame): DataFrame de clientes generado previamente
        versiones_df (pd.DataFrame): DataFrame de versiones generado previamente
        n (int): Número de instalaciones a generar. Por defecto 100.

    Retorna:
        pd.DataFrame: DataFrame con columnas:
            - instalacion_id (int): Identificador único de la instalación
            - cliente_id (int): FK → clientes.cliente_id
            - version_id (int): FK → versiones_software.version_id
            - fecha_instalacion (datetime): Fecha en que se instaló
            - nivel_datos_sensibles (str): Nivel de datos sensibles manejados
    """
    print(f"[ROL1] Generando {n} instalaciones...")

    # IDs válidos para garantizar integridad referencial
    clientes_ids = clientes_df['cliente_id'].tolist()
    versiones_ids = versiones_df['version_id'].tolist()

    # Probabilidades de versión (más instalaciones de versiones comprometidas,
    # siguiendo el patrón del caso real)
    version_probs = [0.15, 0.10, 0.08, 0.07, 0.10, 0.25, 0.15, 0.10]

    instalaciones = []
    for i in range(1, n + 1):
        version_id = np.random.choice(versiones_ids, p=version_probs)
        cliente_id = np.random.choice(clientes_ids)

        # La fecha de instalación debe ser posterior al release de la versión
        version_row = versiones_df[versiones_df['version_id'] == version_id].iloc[0]
        fecha_release = version_row['fecha_release']

        # Instalación entre 1 y 90 días después del release
        dias_despues = np.random.randint(1, 91)
        fecha_instalacion = fecha_release + timedelta(days=int(dias_despues))

        # Limitar al rango del caso (hasta marzo 2021)
        fecha_max = datetime(2021, 3, 31)
        if fecha_instalacion > fecha_max:
            fecha_instalacion = fecha_max - timedelta(days=np.random.randint(1, 30))

        # Nivel de datos sensibles correlacionado con criticidad del cliente
        criticidad_cliente = clientes_df[clientes_df['cliente_id'] == cliente_id]['criticidad'].iloc[0]
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

    # Estadísticas de instalaciones con SUNBURST
    versiones_sunburst = versiones_df[versiones_df['contiene_sunburst'] == True]['version_id'].tolist()
    n_sunburst = df[df['version_id'].isin(versiones_sunburst)].shape[0]
    print(f"    ✓ {len(df)} instalaciones generadas ({n_sunburst} con versiones SUNBURST)")

    return df


def guardar_csvs(clientes_df, versiones_df, instalaciones_df, ruta='../data/'):
    """
    Guarda los DataFrames generados como archivos CSV en la carpeta de datos.

    Parámetros:
        clientes_df (pd.DataFrame): DataFrame de clientes
        versiones_df (pd.DataFrame): DataFrame de versiones
        instalaciones_df (pd.DataFrame): DataFrame de instalaciones
        ruta (str): Ruta de la carpeta de destino. Por defecto '../data/'
    """
    # Crear directorio si no existe
    os.makedirs(ruta, exist_ok=True)

    # Guardar cada DataFrame
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
    print("=" * 70)
    print()

    # Determinar la ruta de datos relativa al script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    # 1. Generar datos
    clientes = generar_clientes(n=50)
    print()

    versiones = generar_versiones()
    print()

    instalaciones = generar_instalaciones(clientes, versiones, n=100)
    print()

    # 2. Mostrar vista previa
    print("-" * 70)
    print("VISTA PREVIA DE LOS DATOS GENERADOS")
    print("-" * 70)
    print("\n📋 Clientes (primeros 5):")
    print(clientes.head().to_string(index=False))
    print(f"\n📋 Versiones Software:")
    print(versiones.to_string(index=False))
    print(f"\n📋 Instalaciones (primeros 5):")
    print(instalaciones.head().to_string(index=False))

    # 3. Guardar CSVs
    print()
    guardar_csvs(clientes, versiones, instalaciones, ruta=data_dir)
