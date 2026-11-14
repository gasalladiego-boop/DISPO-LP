@st.cache_data(ttl=60)
def cargar_datos_cruce():
    # Opción más directa si compartes la hoja de Google Sheets como "Cualquier persona con el enlace puede ver":
    sheet_id = "TU_SHEET_ID_AQUI" # El ID largo que aparece en la URL de tu Google Sheet
    sheet_name = "Resultado_Cruce"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    df = pd.read_csv(url)
    return df
