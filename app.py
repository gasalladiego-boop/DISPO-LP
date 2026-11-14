import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la página
st.set_page_config(
    page_title="Control Operativo - Despacho de Técnicos",
    page_icon="🚀",
    layout="wide"
)

# Título principal
st.title("📊 Panel Operativo de Campo")
st.markdown("Cruce en tiempo real: **Capacidad de Técnicos vs. Tareas Activas (Salesforce)**")

# Función para conectar a Google Sheets (usando tus credenciales de servicio o caché)
@st.cache_data(ttl=60) # Se actualiza solo cada 1 minuto
def cargar_datos_cruce():
    # Nota: Aquí puedes conectar tu Google Sheet mediante gspread o leer directo un CSV exportado
    # Ejemplo conectando a la solapa 'Resultado_Cruce' generada por tu Apps Script:
    # ---------------------------------------------------------
    # scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets']
    # creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    # client = gspread.authorize(creds)
    # sheet = client.open("Tu_Nombre_De_Google_Sheet").worksheet("Resultado_Cruce")
    # data = sheet.get_all_records()
    # df = pd.DataFrame(data)
    # ---------------------------------------------------------
    
    # Simulación de estructura para que veas cómo queda visualmente:
    data = {
        "ID Técnico": ["12LPR024", "12LPE009", "12LPR045", "12LPE001", "12LPR011"],
        "Nombre": ["Fernando Ma...", "Javier Alejan...", "Leandro Gab...", "Domingo Zot...", "Jorge Fabian"],
        "Rotación": ["G9", "G9", "G9", "G4", "G7"],
        "Estado Actual": ["OCUPADO", "LIBRE (Sin Tareas)", "OCUPADO", "LIBRE (Sin Tareas)", "OCUPADO"],
        "Cant. Tareas": [2, 0, 1, 0, 3],
        "Detalle de Tareas": ["RED - HFC (SA-2783262 - Nodo: LA PLATA) | ...", "-", "RED - HFC (SA-2793693 - Nodo: ENSENADA)", "-", "RED - HFC (...)"]
    }
    return pd.DataFrame(data)

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

# --- SECCIÓN CRÍTICA: TÉCNICOS LIBRES (Para reasignar ya) ---
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

# Botón para refrescar datos manualmente
if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()