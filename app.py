import streamlit as st
import pandas as pd

st.set_page_config(page_title="Panel Operativo La Plata", layout="wide")

st.title("🚀 Panel de Control Operativo - La Plata")

# --- CARGA DE DATOS DESDE TUS SOLAPAS DE GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def cargar_datos():
    # ⚠️ REEMPLAZÁ 'TU_GOOGLE_SHEET_ID' por el ID real de tu planilla de Google Sheets
    sheet_id = "TU_GOOGLE_SHEET_ID"
    url_cruce = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Resultado_Cruce"
    url_pendientes = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Pendientes_Asignar"
    
    df_cruce = pd.read_csv(url_cruce)
    df_pendientes = pd.read_csv(url_pendientes)
    return df_cruce, df_pendientes

try:
    df_cruce, df_pendientes = cargar_datos()
except Exception as e:
    st.error(f"Error al conectar con las solapas de Google Sheets: {e}")
    df_cruce = pd.DataFrame()
    df_pendientes = pd.DataFrame()

# --- DISTRIBUCIÓN EN 2 COLUMNAS PARA LA PANTALLA PRINCIPAL ---
col1, col2 = st.columns(2)

# --- COLUMNA 1: MÓVILES LIBRES (Sin Tareas) ---
with col1:
    st.subheader("🟢 Móviles Libres")
    
    if not df_cruce.empty and 'Estado Actual' in df_cruce.columns:
        df_libres = df_cruce[df_cruce['Estado Actual'].str.contains("LIBRE", na=False)]
        
        if not df_libres.empty:
            st.success(f"Disponibles: {len(df_libres)} móviles")
            st.dataframe(df_libres[['ID Técnico', 'Nombre', 'Rotación']], use_container_width=True, hide_index=True)
        else:
            st.info("Todos los móviles se encuentran ocupados en este momento.")
    else:
        st.warning("Cargando datos de móviles...")

# --- COLUMNA 2: RESUMEN DE CITAS SIN ASIGNAR ---
with col2:
    st.subheader("📌 Citas Sin Asignar")
    
    if not df_pendientes.empty:
        total_pendientes = len(df_pendientes)
        st.warning(f"Total pendientes: {total_pendientes}")
        
        # Resumen rápido por tipo de orden (Correctivo, Salud, MPI, Indispo)
        if 'Tipo de Orden' in df_pendientes.columns:
            conteo_tipos = df_pendientes['Tipo de Orden'].value_counts()
            st.write("Desglose por tipo:")
            st.json(conteo_tipos.to_dict(), expanded=False)
    else:
        st.success("¡Sin pendientes de asignación!")

st.markdown("---")

# --- SECCIÓN INFERIOR: TABLA GENERAL DE CITAS SIN ASIGNAR CON FILTROS ---
st.subheader("📋 Detalle de Citas Sin Asignar (Correctivos, Salud, MPI, Indisponibilidad)")

if not df_pendientes.empty:
    if 'Tipo de Orden' in df_pendientes.columns:
        tipos_disponibles = df_pendientes['Tipo de Orden'].unique()
        filtro_tipo = st.multiselect("Filtrar por Tipo de Tarea:", options=tipos_disponibles, default=tipos_disponibles)
        
        df_filtrado = df_pendientes[df_pendientes['Tipo de Orden'].isin(filtro_tipo)]
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_pendientes, use_container_width=True, hide_index=True)
else:
    st.success("¡Excelente! No hay citas pendientes sin asignar en este momento.")
