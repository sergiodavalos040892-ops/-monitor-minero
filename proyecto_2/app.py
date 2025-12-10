import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster, MarkerCluster
import data_loader
import analysis
import os

# Configuración de la página
st.set_page_config(layout="wide", page_title="Análisis de Impacto Minero")

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

# CSS Personalizado para acentos
st.markdown("""
<style>
    /* Color de acento naranja para métricas y elementos destacados */
    [data-testid="stMetricValue"] {
        color: #D98D30 !important;
    }
    
    /* Pestañas seleccionadas */
    .stTabs [aria-selected="true"] {
        color: #D98D30 !important;
        border-top-color: #D98D30 !important;
    }
    
    /* Bordes de inputs al enfocar */
    .stTextInput input:focus {
        border-color: #D98D30 !important;
        box-shadow: 0 0 0 1px #D98D30 !important;
    }
</style>
""", unsafe_allow_html=True)
BDPI_PATH = os.path.join(DATA_DIR, 'bdpi.xlsx')
MINAS_PATH = os.path.join(DATA_DIR, 'minas.xlsx')
DEP_DIR = os.path.join(DATA_DIR, 'departamentos')

# Carga de Datos (Cacheada)
@st.cache_data
def load_all_data():
    with st.spinner('Cargando datos...'):
        bdpi = data_loader.load_bdpi(BDPI_PATH)
        minas = data_loader.load_minas(MINAS_PATH)
        deps = data_loader.load_departamentos(DEP_DIR)
    return bdpi, minas, deps

bdpi, minas, deps = load_all_data()

# --- Sidebar ---
st.sidebar.title("Configuración")
radius_km = st.sidebar.slider("Radio de Influencia (km)", min_value=1, max_value=100, value=10, step=1)

st.sidebar.divider()
st.sidebar.subheader("Filtros de Ubicación")

# Lógica de Filtros en Cascada
# 1. Filtro Departamento
# Obtenemos departamentos únicos de ambos datasets para tener una lista completa
deptos_bdpi = bdpi['departamento'].dropna().unique() if bdpi is not None else []
deptos_minas = minas['departamento'].dropna().unique() if minas is not None else []
all_deptos = sorted(list(set(deptos_bdpi) | set(deptos_minas)))

selected_depto = st.sidebar.multiselect("Departamento", options=all_deptos)

# Filtrado preliminar para opciones siguientes
idx_bdpi = bdpi.index
idx_minas = minas.index

if selected_depto:
    idx_bdpi = bdpi[bdpi['departamento'].isin(selected_depto)].index
    idx_minas = minas[minas['departamento'].isin(selected_depto)].index

# 2. Filtro Provincia (Basado en Depto)
provs_bdpi = bdpi.loc[idx_bdpi, 'provincia'].dropna().unique()
provs_minas = minas.loc[idx_minas, 'provincia'].dropna().unique()
all_provs = sorted(list(set(provs_bdpi) | set(provs_minas)))

selected_prov = st.sidebar.multiselect("Provincia", options=all_provs)

if selected_prov:
    # Refinamos índices
    idx_bdpi = bdpi.loc[idx_bdpi][bdpi.loc[idx_bdpi, 'provincia'].isin(selected_prov)].index
    idx_minas = minas.loc[idx_minas][minas.loc[idx_minas, 'provincia'].isin(selected_prov)].index

# 3. Filtro Distrito (Basado en Prov)
dists_bdpi = bdpi.loc[idx_bdpi, 'distrito'].dropna().unique()
dists_minas = minas.loc[idx_minas, 'distrito'].dropna().unique()
all_dists = sorted(list(set(dists_bdpi) | set(dists_minas)))

selected_dist = st.sidebar.multiselect("Distrito", options=all_dists)

if selected_dist:
    idx_bdpi = bdpi.loc[idx_bdpi][bdpi.loc[idx_bdpi, 'distrito'].isin(selected_dist)].index
    idx_minas = minas.loc[idx_minas][minas.loc[idx_minas, 'distrito'].isin(selected_dist)].index

# 4. Filtro Unidad Minera (Específico)
minas_disponibles = sorted(minas.loc[idx_minas, 'unidad_minera'].unique())
selected_mina = st.sidebar.multiselect("Unidad Minera", options=minas_disponibles)

if selected_mina:
    idx_minas = minas.loc[idx_minas][minas.loc[idx_minas, 'unidad_minera'].isin(selected_mina)].index

# 5. Filtro Centro Poblado (Específico)
# Limitamos opciones a lo ya filtrado para no saturar
cps_disponibles = sorted(bdpi.loc[idx_bdpi, 'nombre_cp'].unique())
# Usamos selectbox con busqueda o multiselect. Multiselect vacio = todos.
selected_cp = st.sidebar.multiselect("Centro Poblado", options=cps_disponibles)

if selected_cp:
    idx_bdpi = bdpi.loc[idx_bdpi][bdpi.loc[idx_bdpi, 'nombre_cp'].isin(selected_cp)].index


# APLICAR FILTROS FINALES
bdpi_filtered = bdpi.loc[idx_bdpi].copy()
minas_filtered = minas.loc[idx_minas].copy()

# Filtros visuales opcionales
st.sidebar.divider()
st.sidebar.subheader("Capas")
show_all_locs = st.sidebar.checkbox("Ver TODAS las localidades (Filtradas)", value=False)
radius_km = float(radius_km) # Asegurar float

# --- Análisis con datos filtrados ---
if not minas_filtered.empty and not bdpi_filtered.empty:
    results = analysis.calculate_impact(minas_filtered, bdpi_filtered, radius_km)
    
    impact_df = results['impact_per_mine']
    global_stats = results['global_stats']
    buffers_gdf = results['minas_buffered']
    affected_locs_gdf = results['affected_localities']
elif minas_filtered.empty:
    st.warning("No hay unidades mineras que coincidan con los filtros seleccionados.")
    st.stop()
else:
    # No hay BDPI pero sí minas (puede pasar en zonas sin poblacion indigena)
    results = analysis.calculate_impact(minas_filtered, bdpi_filtered, radius_km) # Maneja dataframes vacios
    impact_df = results['impact_per_mine']
    global_stats = results['global_stats']
    buffers_gdf = results['minas_buffered']
    affected_locs_gdf = results['affected_localities']


# --- Layout Principal ---
st.title("Monitor de Impacto Social Minero")
st.caption(f"Mostrando {len(minas_filtered)} minas y {len(bdpi_filtered)} localidades según filtros.")

# Métricas Globales (Top) - Comunes a ambas vistas
col1, col2 = st.columns(2)
col1.metric("Total Localidades Afectadas", f"{global_stats['total_locs']:,}")
col2.metric("Población Afectada (Aprox.)", f"{global_stats['total_pop']:,}")

# Pestañas de Navegación
tab_mapa, tab_matriz = st.tabs(["🗺️ Mapa Interactivo", "📋 Matriz de Datos"])

# --- VISTA 1: MAPA ---
with tab_mapa:
    col_map, col_report = st.columns([2, 1])

    with col_map:
        st.subheader("Visualización Geoespacial")
        # Centro aproximado de Perú
        m = folium.Map(location=[-9.19, -75.015], zoom_start=5, tiles="CartoDB positron")
        
        # 1. Capa Departamentos
        if deps is not None:
            folium.GeoJson(
                deps,
                name="Departamentos",
                style_function=lambda x: {'fillColor': '#ffffff00', 'color': 'gray', 'weight': 1}
            ).add_to(m)
        
        # 2. Capa Todas las Localidades (Opcional o Clustered)
        if show_all_locs and not bdpi_filtered.empty:
            # Usamos FastMarkerCluster para optimizar
            FastMarkerCluster(
                data=list(zip(bdpi_filtered.geometry.y, bdpi_filtered.geometry.x)),
                name="Todas las Localidades (Filtradas)"
            ).add_to(m)

        # 3. Capa Localidades Afectadas (Puntos destacados)
        if not affected_locs_gdf.empty:
            # GeoJson con CircleMarker
            folium.GeoJson(
                affected_locs_gdf,
                name="Localidades Afectadas",
                marker=folium.CircleMarker(radius=3, fill_color="orange", fill_opacity=0.7, color="black", weight=0.5),
                tooltip=folium.GeoJsonTooltip(fields=['nombre_cp', 'poblacion'], aliases=['Localidad:', 'Población:'])
            ).add_to(m)

        # 4. Capas Buffers
        if buffers_gdf is not None:
            folium.GeoJson(
                buffers_gdf,
                name="Radio de Influencia",
                style_function=lambda x: {'fillColor': 'red', 'color': 'red', 'weight': 1, 'fillOpacity': 0.2}
            ).add_to(m)

        # 5. Capa Minas
        if not minas_filtered.empty:
            for idx, row in minas_filtered.iterrows():
                folium.Marker(
                    location=[row.geometry.y, row.geometry.x],
                    popup=row['unidad_minera'],
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)

        folium.LayerControl().add_to(m)
        st_folium(m, width=None, height=600, use_container_width=True)
        st.caption("Fuente: Elaboración propia.")

    with col_report:
        st.subheader("Ranking de Impacto")
        if not impact_df.empty:
            # Formatear tabla
            display_df = impact_df.copy()
            display_df.columns = ['Unidad Minera', 'N° Localidades', 'Población Afectada']
            
            st.dataframe(
                display_df.style.background_gradient(subset=['Población Afectada'], cmap="Reds"),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay localidades afectadas en este radio.")

# --- VISTA 2: MATRIZ ---
with tab_matriz:
    st.subheader("Detalle de Impacto: Relación Mina - Localidad")
    
    detailed_data = results.get('detailed_match')
    
    if detailed_data is not None and not detailed_data.empty:
        # Seleccionar y ordenar columnas para la vista matricial
        # columnas disponibles vienen del merge (bdpi + minas)
        # Identificamos columnas clave. 'nombre_cp', 'unidad_minera', 'poblacion', 'departamento_left' (bdpi), etc.
        # Al hacer sjoin, si hay colisiones agrega sufijos.
        
        cols_display = []
        # Buscamos columnas inteligentes
        all_cols = detailed_data.columns.tolist()
        
        col_mina = 'unidad_minera' 
        col_cp = 'nombre_cp'
        col_pob = 'poblacion'
        
        # Depto/Prov/Dist pueden duplicarse. Priorizamos los de la localidad (BDPI) que suelen estar a la izquierda por default en sjoin(bdpi, minas)
        # pero geopandas sjoin mantiene geometría izquierda.
        col_dpto = 'departamento_left' if 'departamento_left' in all_cols else 'departamento'
        col_prov = 'provincia_left' if 'provincia_left' in all_cols else 'provincia'
        col_dist = 'distrito_left' if 'distrito_left' in all_cols else 'distrito'
        
        final_cols = [col_mina, col_cp, col_pob, col_dpto, col_prov, col_dist]
        
        # Filtramos solo las que existen
        final_cols = [c for c in final_cols if c in all_cols]
        
        matrix_df = pd.DataFrame(detailed_data[final_cols])
        
        # Renombrar para presentación bonita
        rename_map = {
            col_mina: 'Unidad Minera',
            col_cp: 'Centro Poblado Afectado',
            col_pob: 'Población',
            col_dpto: 'Departamento (CP)',
            col_prov: 'Provincia (CP)',
            col_dist: 'Distrito (CP)'
        }
        matrix_df = matrix_df.rename(columns=rename_map)
        
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)
        
        # Botón de Descarga
        # Convertir a CSV
        csv = matrix_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Descargar Matriz en CSV",
            data=csv,
            file_name='matriz_impacto_minero.csv',
            mime='text/csv',
        )
    else:
        st.info("No hay datos detallados para mostrar con los filtros actuales.")

st.markdown("---")
st.markdown("**Fuente:** Elaboración propia.")
