"""
=============================================================================
ROL 3: Integrador de Datos - Consolidación y Mapeo al Ciclo de Vida
=============================================================================
Caso SUNBURST - Análisis de Gestión de Datos
Universidad de San Buenaventura | Gestión de Datos | 3er Semestre

PENDIENTE: Este script se completará en la siguiente fase del proyecto.

Funciones planificadas:
  - cargar_datos(): Cargar todos los CSVs de Rol 1 y Rol 2
  - integrar_datos(): Usar pandas merge() para consolidar DataFrames
  - mapear_ciclo_vida(): Asignar fases del ciclo de vida a eventos
  - crear_dashboard(): Generar dashboard visual integrado
=============================================================================
"""

# TODO: Implementar funciones de integración

import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Cargar datos
# =========================
clientes = pd.read_csv("data/clientes.csv")
instalaciones = pd.read_csv("data/instalaciones.csv")
versiones = pd.read_csv("data/versiones_software.csv")
eventos = pd.read_csv("data/eventos_seguridad.csv")

# =========================
# Limpieza básica
# =========================
instalaciones["nivel_datos_sensibles"] = instalaciones[
    "nivel_datos_sensibles"
].fillna("Desconocido")

versiones["fecha_release"] = versiones["fecha_release"].fillna("No registrada")

# =========================
# Integración
# =========================
df = instalaciones.merge(clientes, on="cliente_id", how="left")
df = df.merge(versiones, on="version_id", how="left")
df = df.merge(eventos, on="instalacion_id", how="left")

print("Dataset consolidado:", df.shape)

# =========================
# Validaciones de integración
# =========================
df["cliente_invalido"] = df["cliente_id"].isin([888, 999])
df["version_invalida"] = ~df["version_id"].isin(versiones["version_id"])

# =========================
# Mapeo ciclo de vida
# =========================
mapa_ciclo = {
    "reconocimiento": "Descubrimiento",
    "acceso_normal": "Operación",
    "descarga_datos": "Uso",
    "alerta_ids": "Monitoreo",
    "movimiento_lateral": "Incidente",
    "persistencia": "Mantenimiento",
    "exfiltracion": "Compromiso",
    "conexion_c2": "Compromiso",
    "modificacion_logs": "Auditoría",
    "escalamiento_privilegios": "Incidente"
}

mapa_dama = {
    "Descubrimiento": "Data Architecture",
    "Operación": "Data Operations",
    "Uso": "Data Security",
    "Monitoreo": "Data Governance",
    "Incidente": "Data Quality",
    "Mantenimiento": "Data Integration",
    "Compromiso": "Data Security",
    "Auditoría": "Metadata Management"
}

df["fase_ciclo_vida"] = df["tipo_evento"].map(mapa_ciclo)
df["area_dama"] = df["fase_ciclo_vida"].map(mapa_dama)

# =========================
# Export 1: eventos ciclo vida
# =========================
eventos_ciclo = df[
    [
        "evento_id",
        "timestamp",
        "tipo_evento",
        "fase_ciclo_vida",
        "area_dama"
    ]
]

eventos_ciclo.to_csv("data/eventos_ciclo_vida.csv", index=False)

# =========================
# Export 2: resumen impacto
# =========================
resumen = df.groupby("nombre_version").agg(
    total_instalaciones=("instalacion_id", "nunique"),
    clientes_expuestos=("cliente_id", "nunique"),
    versiones_vulnerables=("contiene_sunburst", "sum"),
    eventos_criticos=("severidad", lambda x: (x == "Crítica").sum()),
    anomalias=("es_anomalo", "sum")
).reset_index()

resumen.to_csv("data/resumen_impacto.csv", index=False)

# =========================
# Dashboard gráfico
# =========================
conteo = df["fase_ciclo_vida"].value_counts()

plt.figure(figsize=(10, 6))
conteo.plot(kind="bar")
plt.title("Distribución de eventos por fase del ciclo de vida")
plt.xlabel("Fase")
plt.ylabel("Cantidad")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("visualizations/dashboard_integrado.png")
plt.close()

print("Rol 3 ejecutado correctamente.")
