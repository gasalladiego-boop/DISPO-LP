import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Panel Operativo La Plata", layout="wide")

st.title("🚀 Panel de Control Operativo - La Plata")

# --- CARGA DE DATOS ROBUSTA DESDE GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def cargar_datos():
    sheet_id = "1Ai1ykoeHgL8W1R77pJj6wjke2Sd-GuaFq1G9bx7vmEs"
    
    url_cruce = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Resultado_Cruce"
    url_pendientes = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Pendientes_Asignar"
    
    try:
        df_cruce = pd.read_csv(url_cruce, on_bad_lines='skip')
    except Exception:
        df_cruce = pd.DataFrame()
        
    try:
        df_pendientes = pd.read_csv(url_pendientes, on_bad_lines='skip')
    except Exception:
        df_pendientes = pd.DataFrame()
        
    return df_cruce, df_pendientes

try:
    df_cruce, df_pendientes = cargar_datos()
except Exception as e:
    st.error(f"Error al conectar con las solapas de Google Sheets: {e}")
    df_cruce = pd.DataFrame()
    df_pendientes = pd.DataFrame()

# Limpieza de columnas
if not df_cruce.empty:
    df_cruce.columns = df_cruce.columns.str.strip()
if not df_pendientes.empty:
    df_pendientes.columns = df_pendientes.columns.str.strip()
    if len(df_pendientes.columns) >= 4:
        df_pendientes.columns = ['Tipo de Orden', 'Appointment', 'Nodo HFC', 'Estado']

# --- ASIGNACIÓN INTELIGENTE DE TURNO (MAÑANA / TARDE) ---
moviles_tarde = [
    "12LPR026", "12LPR028", "12LPR035", "12LPR046", 
    "12LPR040", "12LPR048", "12LPR002", "12LPR047", 
    "12LPR039", "12LPR003"
]

def asignar_turno(id_tec):
    if pd.isna(id_tec):
        return "Mañana"
    id_limpio = str(id_tec).strip()
    return "Tarde" if id_limpio in moviles_tarde else "Mañana"

if not df_cruce.empty and 'ID Técnico' in df_cruce.columns:
    df_cruce['Turno'] = df_cruce['ID Técnico'].apply(asignar_turno)

# --- LIMPIEZA DE DETALLE DE TAREAS PARA MOSTRAR CORTO Y SEPARADO ---
def limpiar_detalle_tareas(detalle):
    if pd.isna(detalle) or not str(detalle).strip():
        return "-", "-"
    
    texto = str(detalle).split('|')[0].strip()
    
    match_nodo = re.search(r'Nodo:\s*([A-Z0-9]+)', texto)
    nodo_limpio = match_nodo.group(1) if match_nodo else "-"
    
    actividad_corta = re.sub(r'\(Nodo:.*?\)', '', texto).replace('- HFC -', '-').strip()
    if actividad_corta.endswith('-'):
        actividad_corta = actividad_corta[:-1].strip()
        
    return actividad_corta, nodo_limpio

if not df_cruce.empty and 'Detalle de Tareas' in df_cruce.columns:
    resultados_limpios = df_cruce['Detalle de Tareas'].apply(limpiar_detalle_tareas)
    df_cruce['Actividad'] = [r[0] for r in resultados_limpios]
    df_cruce['Nodo HFC'] = [r[1] for r in resultados_limpios]


# --- SECCIÓN PRINCIPAL: MÓVILES LIBRES Y OCUPADOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🟢 Móviles Libres")
    if not df_cruce.empty and 'Estado Actual' in df_cruce.columns:
        df_libres = df_cruce[df_cruce['Estado Actual'].str.contains("LIBRE", na=False)]
        if not df_libres.empty:
            st.success(f"Disponibles: {len(df_libres)} móviles")
            st.dataframe(df_libres[['Turno', 'ID Técnico', 'Nombre', 'Rotación']], use_container_width=True, hide_index=True)
        else:
            st.info("Todos los móviles se encuentran ocupados.")
    else:
        st.warning("Cargando datos de móviles...")

with col2:
    st.subheader("🚗 Móviles Ocupados (Con Actividad)")
    if not df_cruce.empty and 'Estado Actual' in df_cruce.columns:
        df_ocupados = df_cruce[df_cruce['Estado Actual'].str.contains("OCUPADO", na=False)]
        if not df_ocupados.empty:
            st.warning(f"Ocupados: {len(df_ocupados)} móviles")
            st.dataframe(
                df_ocupados[['Turno', 'ID Técnico', 'Nombre', 'Actividad', 'Nodo HFC', 'Cant. Tareas']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No hay móviles ocupados.")

st.markdown("---")

# --- SECCIÓN DE CITAS SIN ASIGNAR (Corregido sin error de sintaxis) ---
st.subheader("📋 Detalle de Citas Sin Asignar (Correctivos, Salud, MPI, Indisponibilidad)")

if not df_pendientes.empty:
    total_pendientes = len(df_pendientes)
    st.info(f"Total de citas pendientes de asignación en este momento: **{total_pendientes}**")
    
    if 'Tipo de Orden' in df_pendientes.columns:
        tipos_disponibles = df_pendientes['Tipo de Orden'].unique()
        filtro_tipo = st.multiselect("Filtrar por Tipo de Tarea:", options=tipos_disponibles, default=tipos_disponibles)
        
        df_filtrado = df_pendientes[df_pendientes['Tipo de Orden'].isin(filtro_tipo)]
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_pendientes, use_container_width=True, hide_index=True)
else:
    st.success("¡Excelente! No hay citas pendientes sin asignar en este momento.")
# Ejemplo de filtrado seguro y tolerante a fallos para tus DataFrames en Streamlit
columnas_deseadas = ['Turno', 'ID Técnico', 'Nombre', 'Actividad', 'Activity', 'Nodo HFC', 'Cant. Tareas', 'Detalle de Tareas / Motivo Ausencia', 'Estado Actual']

# Verificamos y seleccionamos dinámicamente solo las columnas que existan en el DataFrame
columnas_existentes = [col for col in columnas_deseadas if col in df_ocupados.columns]

# Generamos el DataFrame visual sin riesgo de KeyError
df_ocupados_visual = df_ocupados[columnas_existentes]
