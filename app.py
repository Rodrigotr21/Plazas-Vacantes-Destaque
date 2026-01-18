import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Monitor de Plazas 2026", layout="wide", page_icon="🇵🇪")

# --- 1. CARGA DE DATOS PRINCIPALES ---
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv("data_plazas_completa.csv")
        df.fillna("SIN INFORMACIÓN", inplace=True)
        # Limpieza estándar
        if 'PROVINCIA' in df.columns:
            df['PROVINCIA'] = df['PROVINCIA'].astype(str).str.strip().str.upper()
        if 'DISTRITO' in df.columns:
            df['DISTRITO'] = df['DISTRITO'].astype(str).str.strip().str.upper()
        return df
    except FileNotFoundError:
        return None

# --- 2. CARGA DE COORDENADAS DISTRITALES (NUEVO) ---
@st.cache_data
def cargar_coords_distritos():
    try:
        # Intenta cargar el archivo generado en el Paso 1
        df_coords = pd.read_csv("coords_distritos.csv")
        return df_coords
    except FileNotFoundError:
        return None

df_raw = cargar_datos()
df_coords_dist = cargar_coords_distritos()

if df_raw is None:
    st.error("⚠️ Error: No encuentro 'data_plazas_completa.csv'.")
    st.stop()

df = df_raw.copy()

# DETECCIÓN DE COLUMNA NOMBRE
col_nombre = 'NOMBRE_IE'
if col_nombre not in df.columns:
    posibles = [c for c in df.columns if 'NOMBRE' in c or 'INSTITUCION' in c or 'I.E.' in c]
    col_nombre = posibles[0] if posibles else 'NOMBRE_IE'

# --- TÍTULO ---
st.title(f"🇵🇪 Monitor de Vacantes: {len(df):,} Plazas Disponibles")
st.markdown("---")

# --- 3. FILTROS (SIDEBAR) ---
st.sidebar.header("🔍 Filtros de Búsqueda")

# Filtros Jerárquicos
lista_provincias = sorted(df['PROVINCIA'].unique())
prov = st.sidebar.multiselect("Provincia", lista_provincias)
if prov:
    df = df[df['PROVINCIA'].isin(prov)]

# Filtro Distrito (dinámico)
lista_distritos = sorted(df[df['PROVINCIA'].isin(prov)]['DISTRITO'].unique()) if prov else sorted(df['DISTRITO'].unique())
dist = st.sidebar.multiselect("Distrito", lista_distritos)
if dist:
    df = df[df['DISTRITO'].isin(dist)]

# Otros filtros
if 'NIVEL_EDUCATIVO' in df.columns: 
    # Ajusta 'NIVEL_EDUCATIVO' al nombre real de tu columna de nivel
    col_nivel = 'NIVEL_EDUCATIVO'
else:
    # Búsqueda fallback
    col_nivel = [c for c in df.columns if 'NIVEL' in c][0]

nivel = st.sidebar.multiselect("Nivel", sorted(df[col_nivel].astype(str).unique()))
if nivel:
    df = df[df[col_nivel].isin(nivel)]

if 'TIPO_VACANTE' in df.columns:
    tipo = st.sidebar.multiselect("Tipo Vacante", sorted(df['TIPO_VACANTE'].astype(str).unique()))
    if tipo:
        df = df[df['TIPO_VACANTE'].isin(tipo)]

# --- 4. DICCIONARIO DE PROVINCIAS (BACKUP) ---
# Se mantiene por si falla el archivo de distritos o para la vista provincial
coords_provincias = {
    'LIMA': [-12.0464, -77.0428], 'CALLAO': [-12.0508, -77.1260], 'AREQUIPA': [-16.3989, -71.5350],
    'TRUJILLO': [-8.1160, -79.0300], 'CHICLAYO': [-6.7714, -79.8409], 'PIURA': [-5.1945, -80.6328],
    'MAYNAS': [-3.7437, -73.2516], 'HUANCAYO': [-12.0681, -75.2100], 'CUSCO': [-13.5320, -71.9675],
    'ICA': [-14.0678, -75.7286], 'PUNO': [-15.8402, -70.0219], 'TACNA': [-18.0146, -70.2536],
    'HUANUCO': [-9.9306, -76.2422], 'CAJAMARCA': [-7.1638, -78.5003], 'SANTA': [-9.0762, -78.5916],
    'CORONEL PORTILLO': [-8.3791, -74.5539], 'HUAURA': [-11.1070, -77.6105], 'HUAMANGA': [-13.1588, -74.2239],
    'TAMBOPATA': [-12.5933, -69.1891], 'HUARAL': [-11.4956, -77.2089], 'CAÑETE': [-13.0760, -76.3860],
    'JAEN': [-5.7061, -78.8080], 'SAN ROMAN': [-15.4906, -70.1342],
    'ILO': [-17.6394, -71.3375], 'PAITA': [-5.0892, -81.1144], 'TALARA': [-4.5772, -81.2719],
    'CHINCHA': [-13.4182, -76.1360], 'PISCO': [-13.7058, -76.2025], 'ABANCAY': [-13.6339, -72.8814],
    'ANDAHUAYLAS': [-13.6558, -73.3872], 'PASCO': [-10.6675, -76.2567], 'HUANCAVELICA': [-12.7861, -74.9760],
    'MOYOBAMBA': [-6.0628, -76.9757], 'TARAPOTO': [-6.4912, -76.3689], 'SAN MARTIN': [-6.4912, -76.3689],
    'TUMBES': [-3.5669, -80.4515], 'ZARUMILLA': [-3.5000, -80.2667], 'MARISCAL NIETO': [-17.1983, -70.9357],
    'CHACHAPOYAS': [-6.2317, -77.8690], 'UTCUBAMBA': [-5.7483, -78.4383], 'BARRANCA': [-10.7514, -77.7606],
    'CHANCHAMAYO': [-11.0560, -75.3283], 'SATIPO': [-11.2522, -74.6385], 'LAMBAYEQUE': [-6.7011, -79.9062],
    'FERREÑAFE': [-6.6375, -79.7892], 'CUTERVO': [-6.3770, -78.8155], 'CHOTA': [-6.5564, -78.6508],
    'HUANTA': [-12.9344, -74.2486], 'LA CONVENCION': [-12.8636, -72.6961], 'URUBAMBA': [-13.3050, -72.1158],
    'ESPINAR': [-14.7933, -71.4089], 'AZANGARO': [-14.9125, -70.1969], 'CHUCUITO': [-16.2414, -69.2964],
    'YUNGUYO': [-16.2444, -69.0961], 'LAMPA': [-15.3622, -70.3664], 'MELGAR': [-14.8833, -70.6500],
    'ALTO AMAZONAS': [-5.8944, -76.1189], 'REQUENA': [-5.0617, -73.8444], 'UCAYALI': [-8.3791, -74.5539],
    'SULLANA': [-4.9039, -80.6853], 'MORROPON': [-5.1814, -79.9686], 'AYABACA': [-4.6392, -79.7142],
    'HUANCABAMBA': [-5.2386, -79.4503], 'SECHURA': [-5.5569, -80.8222], 'CONTRALMIRANTE VILLAR': [-3.9536, -80.6436],
    'BONGARA': [-5.9525, -77.7925], 'LUYA': [-6.1633, -77.9456], 'RODRIGUEZ DE MENDOZA': [-6.3117, -77.4697],
    'HUARAZ': [-9.5278, -77.5278], 'YUNGAY': [-9.1419, -77.7444], 'CARHUAZ': [-9.2819, -77.6453],
    'HUAYLAS': [-8.8703, -77.8592], 'RECUAY': [-9.7214, -77.4533], 'BOLOGNESI': [-10.1556, -77.1458],
    'POMABAMBA': [-8.8197, -77.4611], 'PALLASCA': [-8.4069, -78.0164], 'CASMA': [-9.4725, -78.3100],
    'HUARMEY': [-10.0681, -78.1522], 'ANTABAMBA': [-14.3639, -72.8803],
    'AYMARAES': [-14.0758, -73.1092], 'COTABAMBAS': [-13.9317, -72.3364], 'GRAU': [-14.0933, -72.6369],
    'CAMANA': [-16.6236, -72.7111], 'ISLAY': [-17.0189, -72.0161], 'CAYLLOMA': [-15.6322, -71.6033],
    'CASTILLA': [-15.5414, -72.4286], 'CONDESUYOS': [-15.8367, -72.8553], 'LA UNION': [-15.2936, -72.9303],
    'CANGALLO': [-13.6283, -74.1436], 'LUCANAS': [-14.4753, -74.1203], 'PARINACOCHAS': [-15.1433, -73.6694],
    'PAUCAR DEL SARA SARA': [-15.2789, -73.2842], 'SUCRE': [-13.9939, -73.9556], 'VICTOR FAJARDO': [-13.8211, -74.0739],
    'CELENDIN': [-6.8703, -78.1517], 'CAJABAMBA': [-7.6242, -78.0467], 'CONTUMAZA': [-7.3622, -78.8033],
    'HUALGAYOC': [-6.7561, -78.6186], 'SAN IGNACIO': [-5.1464, -79.0039], 'SAN MARCOS': [-7.3367, -78.1706],
    'SAN MIGUEL': [-7.0011, -78.8508], 'SAN PABLO': [-7.1172, -78.8228], 'SANTA CRUZ': [-6.6258, -78.9453],
    'ACOMAYO': [-13.9189, -71.6842], 'ANTA': [-13.4739, -72.1525], 'CALCA': [-13.3189, -71.9547],
    'CANAS': [-14.2867, -71.4633], 'CANCHIS': [-14.1953, -71.2225], 'CHUMBIVILCAS': [-14.4503, -72.0722],
    'PARURO': [-13.7719, -71.8469], 'PAUCARTAMBO': [-13.3139, -71.5975], 'QUISPICANCHI': [-13.5939, -71.6775],
    'ACOBAMBA': [-12.8425, -74.5714], 'ANGARAES': [-12.9814, -74.7553], 'CASTROVIRREYNA': [-13.2839, -75.3183],
    'CHURCAMPA': [-12.7389, -74.3889], 'HUAYTARA': [-13.6033, -75.3533], 'TAYACAJA': [-12.2356, -74.9142],
    'AMBO': [-10.1308, -76.2047], 'DOS DE MAYO': [-9.8058, -76.7906], 'HUACAYBAMBA': [-9.0397, -76.9422],
    'HUAMALIES': [-9.5544, -76.8153], 'LEONCIO PRADO': [-9.2972, -75.9989], 'MARAÑON': [-8.7183, -76.8322],
    'PACHITEA': [-9.9011, -75.9944], 'PUERTO INCA': [-9.3883, -74.9664], 'LAURICOCHA': [-10.2764, -76.6711],
    'YAROWILCA': [-9.7714, -76.5936], 'NASCA': [-14.8272, -74.9392], 'PALPA': [-14.5336, -75.1856],
    'CONCEPCION': [-11.9189, -75.3131], 'JAUJA': [-11.7758, -75.5006], 'JUNIN': [-11.1581, -75.9935],
    'TARMA': [-11.4189, -75.6897], 'YAULI': [-11.6028, -76.0792], 'CHUPACA': [-12.0633, -75.2825],
    'ASCOPE': [-7.7144, -79.1081], 'BOLIVAR': [-7.1539, -77.7022], 'CHEPEN': [-7.2289, -79.4267],
    'JULCAN': [-8.0436, -78.4908], 'OTUZCO': [-7.9042, -78.5636], 'PACASMAYO': [-7.4019, -79.5714],
    'PATAZ': [-8.2789, -77.3006], 'SANCHEZ CARRION': [-7.8106, -78.0375], 'SANTIAGO DE CHUCO': [-8.1408, -78.1728],
    'GRAN CHIMU': [-7.7733, -78.6539], 'VIRU': [-8.4189, -78.7522], 'CAJATAMBO': [-10.4708, -76.9925],
    'CANTA': [-11.4681, -76.6236], 'HUAROCHIRI': [-11.8389, -76.3811], 'YAUYOS': [-12.4619, -75.9200],
    'OYON': [-10.6692, -76.7711], 'LORETO': [-4.5133, -74.1333], 'MARISCAL RAMON CASTILLA': [-3.9083, -70.5233],
    'PUTUMAYO': [-2.4633, -72.6333], 'MANU': [-12.2708, -70.9014], 'TAHUAMANU': [-11.4019, -69.4897],
    'GENERAL SANCHEZ CERRO': [-16.6358, -70.9575], 'DANIEL ALCIDES CARRION': [-10.4853, -76.5186],
    'OXAPAMPA': [-10.5772, -75.4022], 'CARABAYA': [-13.8219, -70.3606],
    'SANDIA': [-14.3217, -69.4628], 'MOHO': [-15.3611, -69.4981], 'SAN ANTONIO DE PUTINA': [-14.9200, -69.8700],
    'BELLAVISTA': [-7.0561, -76.5911], 'EL DORADO': [-6.5517, -76.7375], 'HUALLAGA': [-6.9942, -76.7628],
    'LAMAS': [-6.4253, -76.5178], 'MARISCAL CACERES': [-7.1706, -76.7958], 'PICOTA': [-6.9192, -76.3308],
    'RIOJA': [-6.0622, -77.1581], 'TOCACHE': [-8.1842, -76.5125], 'CANDARAVE': [-17.2689, -70.2503],
    'JORGE BASADRE': [-17.6253, -70.7078], 'TARATA': [-17.4744, -70.0328], 'ATALAYA': [-10.7292, -73.7581],
    'PADRE ABAD': [-9.0336, -75.5089], 'PURUS': [-9.7708, -70.7083]
}

# --- 5. VISUALIZACIÓN ---
tab1, tab2 = st.tabs(["📊 Mapa y Gráficos", "📋 Detalle de Plazas"])

with tab1:
    st.subheader("🗺️ Mapa de Calor: Concentración de Vacantes")
    
    # Selector de Nivel Geográfico
    nivel_mapa = st.radio("Visualizar mapa por:", ["Provincia", "Distrito"], horizontal=True)
    
    df_mapa_final = pd.DataFrame() # Contenedor vacío
    
    if nivel_mapa == "Provincia":
        # Lógica Original (Provincia)
        df_mapa = df['PROVINCIA'].value_counts().reset_index()
        df_mapa.columns = ['PROVINCIA', 'VACANTES']
        
        def get_lat_lon(prov):
            if prov in coords_provincias:
                return pd.Series(coords_provincias[prov])
            else:
                return pd.Series([None, None])
        
        df_mapa[['LAT', 'LON']] = df_mapa['PROVINCIA'].apply(get_lat_lon)
        df_mapa_final = df_mapa.dropna(subset=['LAT'])
        
    else:
        # Lógica Nueva (Distrito)
        if df_coords_dist is not None:
            # 1. Agrupar por distrito y provincia
            df_mapa = df.groupby(['PROVINCIA', 'DISTRITO']).size().reset_index(name='VACANTES')
            # 2. Unir con las coordenadas cargadas
            df_mapa_final = pd.merge(df_mapa, df_coords_dist, on=['PROVINCIA', 'DISTRITO'], how='left')
            # 3. Renombrar columnas para que coincidan con el mapa
            df_mapa_final.rename(columns={'LAT_DIST': 'LAT', 'LON_DIST': 'LON'}, inplace=True)
            df_mapa_final = df_mapa_final.dropna(subset=['LAT'])
        else:
            st.warning("⚠️ Para ver el mapa por distritos, primero debes generar el archivo 'coords_distritos.csv' con el script proporcionado. Mostrando vista provincial por defecto.")
            # Fallback a provincia si no hay archivo
            nivel_mapa = "Provincia"
            df_mapa = df['PROVINCIA'].value_counts().reset_index()
            df_mapa.columns = ['PROVINCIA', 'VACANTES']
            def get_lat_lon(prov):
                return pd.Series(coords_provincias.get(prov, [None, None]))
            df_mapa[['LAT', 'LON']] = df_mapa['PROVINCIA'].apply(get_lat_lon)
            df_mapa_final = df_mapa.dropna(subset=['LAT'])

    # Graficar
    if not df_mapa_final.empty:
        # Ajustamos el radio dependiendo del nivel de detalle
        radio_punto = 25 if nivel_mapa == "Provincia" else 12
        
        fig_map = px.density_mapbox(
            df_mapa_final,
            lat='LAT',
            lon='LON',
            z='VACANTES',
            radius=radio_punto,
            center=dict(lat=-9.5, lon=-75.0),
            zoom=4.5,
            mapbox_style="carto-positron",
            color_continuous_scale="Viridis",
            hover_name="DISTRITO" if nivel_mapa == "Distrito" else "PROVINCIA",
            title=f"Vacantes por {nivel_mapa}"
        )
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No hay datos geográficos suficientes para los filtros seleccionados.")

    st.markdown("---")

    # --- OTROS GRÁFICOS (Igual que antes) ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏫 Top Colegios")
        df_colegios = df[col_nombre].value_counts().head(15).reset_index()
        df_colegios.columns = ['COLEGIO', 'CANTIDAD']
        fig_col = px.bar(df_colegios, x='COLEGIO', y='CANTIDAD', color='CANTIDAD', color_continuous_scale='Viridis')
        fig_col.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_col, use_container_width=True)

    with col2:
        st.subheader("📍 Top Distritos")
        df_dist = df['DISTRITO'].value_counts().head(15).reset_index()
        df_dist.columns = ['DISTRITO', 'CANTIDAD']
        fig_d = px.bar(df_dist, x='DISTRITO', y='CANTIDAD', color='DISTRITO')
        st.plotly_chart(fig_d, use_container_width=True)

with tab2:
    st.subheader("Listado Detallado")
    cols_base = ['PROVINCIA', 'DISTRITO', 'TIPO_VACANTE', 'NIVEL_EDUCATIVO' if 'NIVEL_EDUCATIVO' in df.columns else 'NIVEL / CICLO / PROGRAMA', 'MOTIVO DE LA VACANCIA', 'CÓDIGO DE PLAZA']
    cols_finales = [col_nombre] + [c for c in cols_base if c in df.columns]
    st.dataframe(df[cols_finales], use_container_width=True, hide_index=True)
