import streamlit as st
import pandas as pd

# Configuración de la página (esto debe ir bien arriba)
st.set_page_config(
    page_title="Control Operativo - Despacho de Técnicos",
    page_icon="🚀",
    layout="wide"
)

# El resto del código de carga de datos y visualización...
@st.cache_data(ttl=60)
def cargar_datos_cruce():
    sheet_id = "T1Ai1ykoeHgL8W1R77pJj6wjke2Sd-GuaFq1G9bx7vmEs/edit?hl=es&gid=74280589#gid=74280589"  # Poné acá el ID de tu Google Sheet
    sheet_name = "Resultado_Cruce"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    return df

df = cargar_datos_cruce()

# --- MÉTRICAS SUPERIORES ---
total_tecnicos = len(df)
libres_df = df[df["Estado Actual"].str.contains("LIBRE")]
ocupados_df = df[~df["Estado Actual"].str.contains("LIBRE")]
cant_libres = len(libres_df)
cant_ocupados = len(ocupados_df)

col1, col2, col3 = st.columns(3)
col1.metric("👷 Técnicos Operativos Hoy", total_tecnicos)
col2.metric("🔴 Técnicos Libres (Sin Tareas)", cant_libres, delta_color="inverse")
col3.metric("🟢 Técnicos Ocupados", cant_ocupados)

st.markdown("---")

# --- SECCIÓN CRÍTICA: TÉCNICOS LIBRES ---
st.subheader("🚨 Personal Disponible para Reasignación Inmediata")
if cant_libres > 0:
    st.warning(f"Hay **{cant_libres} técnicos** operativos que todavía no tienen tareas asignadas en la jornada:")
    for index, row in libres_df.iterrows():
        st.markdown(f"- **{row['ID Técnico']} - {row['Nombre']}** *(Turno: {row['Rotación']})*")
else:
    st.success("✅ ¡Excelente! No hay técnicos ociosos en este momento; todos tienen carga asignada.")

st.markdown("---")

# --- TABLA GENERAL DE ESTADOS ---
st.subheader("📋 Detalle Completo de Recursos y Tareas")
filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "LIBRE (Sin Tareas)", "OCUPADO"])

if filtro_estado != "Todos":
    df_filtrado = df[df["Estado Actual"] == filtro_estado]
else:
    df_filtrado = df

st.dataframe(df_filtrado, use_container_width=True)

if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()
