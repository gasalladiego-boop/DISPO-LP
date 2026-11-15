import streamlit as st
import pandas as pd

st.title("🚀 Panel de Control Operativo - La Plata")

# --- CARGA DE DATOS DESDE TUS SOLAPAS DE GOOGLE SHEETS / FIREBASE ---
# Reemplaza esta sección con tu método actual de conexión (ej: gsheets connection, pandas read_csv, etc.)
@st.cache_data(ttl=60)
def cargar_datos():
    # Ejemplo con enlace público o tu conector de Google Sheets:
    # url_sheet = "TU_ENLACE_DE_GOOGLE_SHEET_O_CSV"
    df_cruce = pd.read_excel("tu_archivo.xlsx", sheet_name="Resultado_Cruce")
    df_pendientes = pd.read_excel("tu_archivo.xlsx", sheet_name="Pendientes_Asignar")
    return df_cruce, df_pendientes

# Inicializamos las variables para que nunca queden en blanco o den NameError
try:
    df_cruce, df_pendientes = cargar_datos()
except Exception as e:
    # Si usas gsheets_connection u otro método, asegúrate de mantener tu línea de lectura original y solo definir df_cruce y df_pendientes aquí arriba.
    st.error(f"Error al cargar los datos de las solapas: {e}")
    df_cruce = pd.DataFrame()
    df_pendientes = pd.DataFrame()

# --- A PARTIR DE ACÁ VA EL RESTO DE TU DISEÑO (COLUMNAS, MÓVILES LIBRES, ETC.) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Móviles Libres")
    if not df_cruce.empty and 'Estado Actual' in df_cruce.columns:
        df_libres = df_cruce[df_cruce['Estado Actual'].str.contains("LIBRE", na=False)]
        if not df_libres.empty:
            st.success(f"Disponibles: {len(df_libres)} móviles")
            st.dataframe(df_libres[['ID Técnico', 'Nombre', 'Rotación']], use_container_width=True, hide_index=True)
        else:
            st.info("Todos los móviles están ocupados.")
    else:
        st.warning("Cargando datos de móviles...")

with col2:
    st.subheader("📌 Citas Sin Asignar")
    if not df_pendientes.empty:
        total_pendientes = len(df_pendientes)
        st.warning(f"Total pendientes: {total_pendientes}")
        if 'Tipo de Orden' in df_pendientes.columns:
            conteo_tipos = df_pendientes['Tipo de Orden'].value_counts()
            st.write("Desglose por tipo:")
            st.json(conteo_tipos.to_dict(), expanded=False)
    else:
        st.success("¡Sin pendientes de asignación!")

st.markdown("---")

st.subheader("📋 Detalle de Citas Sin Asignar (Correctivos, Salud, MPI, Indisponibilidad)")
if not df_pendientes.empty and 'Tipo de Orden' in df_pendientes.columns:
    tipos_disponibles = df_pendientes['Tipo de Orden'].unique()
    filtro_tipo = st.multiselect("Filtrar por Tipo de Tarea:", options=tipos_disponibles, default=tipos_disponibles)
    df_filtrado = df_pendientes[df_pendientes['Tipo de Orden'].isin(filtro_tipo)]
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
elif not df_pendientes.empty:
    st.dataframe(df_pendientes, use_container_width=True, hide_index=True)
else:
    st.success("¡Excelente! No hay citas pendientes sin asignar en este momento.")
