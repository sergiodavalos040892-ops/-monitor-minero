import geopandas as gpd
import pandas as pd

def calculate_impact(minas_gdf, bdpi_gdf, radius_km):
    """
    Calcula el impacto de las minas sobre las localidades indígenas dentro de un radio.
    
    Args:
        minas_gdf (GeoDataFrame): Puntos de minas (EPSG:4326).
        bdpi_gdf (GeoDataFrame): Puntos de localidades (EPSG:4326).
        radius_km (float): Radio de influencia en kilómetros.
        
    Returns:
        dict: {
            'minas_buffered': GeoDataFrame (polígonos de influencia en 4326),
            'impact_per_mine': DataFrame (estadísticas por mina),
            'global_stats': dict (estadísticas globales unicas),
            'affected_localities': GeoDataFrame (localidades afectadas)
        }
    """
    if minas_gdf is None or bdpi_gdf is None or radius_km <= 0:
        return {
            'minas_buffered': minas_gdf, # Return points if no buffer
            'impact_per_mine': pd.DataFrame(),
            'global_stats': {'total_locs': 0, 'total_pop': 0},
            'affected_localities': gpd.GeoDataFrame()
        }

    # 1. Proyectar a UTM 18S (EPSG:32718) para cálculos métricos precisos en Perú
    minas_proj = minas_gdf.to_crs(epsg=32718)
    bdpi_proj = bdpi_gdf.to_crs(epsg=32718)
    
    # 2. Generar buffers
    # radius_km * 1000 para pasar a metros
    buffers_proj = minas_proj.copy()
    buffers_proj['geometry'] = buffers_proj.geometry.buffer(radius_km * 1000)
    
    # 3. Spatial Join
    # Queremos saber qué localidades están dentro de qué buffer de mina.
    # Join 'inner' para quedarnos solo con lo que cruza.
    joined = gpd.sjoin(bdpi_proj, buffers_proj, how='inner', predicate='within')
    
    # 4. Estadísticas por Mina
    # Agrupamos por identificador de mina (asumimos 'unidad_minera' es único o agrupamos por él)
    # Contamos localidades y sumamos población
    impact_per_mine = joined.groupby('unidad_minera').agg(
        num_localidades=('poblacion', 'count'), # count rows
        poblacion_afectada=('poblacion', 'sum')
    ).reset_index()
    
    impact_per_mine = impact_per_mine.sort_values('poblacion_afectada', ascending=False)
    
    # 5. Estadísticas Globales (Deduplicadas)
    # Una localidad puede estar afectada por múltiples minas, pero cuenta como 1 localidad afectada y su gente como población afectada única.
    unique_affected_locs = joined[~joined.index.duplicated(keep='first')]
    
    global_stats = {
        'total_locs': len(unique_affected_locs),
        'total_pop': unique_affected_locs['poblacion'].sum()
    }
    
    # 6. Preparar datos para retorno (reproyectar a 4326 para mapeo)
    buffers_4326 = buffers_proj.to_crs(epsg=4326)
    
    # Limpiar columnas duplicadas o innecesarias para el GeoJSON
    # Nos quedamos solo con lo necesario para el tooltip y el mapa
    # Usamos .copy() para evitar SettingWithCopyWarning
    cols_to_keep = ['geometry', 'poblacion']
    if 'nombre_cp' in unique_affected_locs.columns:
        cols_to_keep.append('nombre_cp')
    
    final_affected_locs = unique_affected_locs[cols_to_keep].copy()

    # Para la Matriz: Necesitamos el join completo (Mina <-> Localidad), no el deduplicado
    # 'joined' tiene geometria de BDPI (puntos) con datos de mina adjuntos.
    match_detailed = joined.to_crs(epsg=4326).copy()
    
    # Retornamos las geometrías de buffers y el resumen
    return {
        'minas_buffered': buffers_4326,
        'impact_per_mine': impact_per_mine,
        'global_stats': global_stats,
        'affected_localities': final_affected_locs.to_crs(epsg=4326),
        'detailed_match': match_detailed
    }
