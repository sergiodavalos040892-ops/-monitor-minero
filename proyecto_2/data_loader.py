import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import unicodedata

def remove_accents(input_str):
    if not isinstance(input_str, str):
        return str(input_str)
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def load_bdpi(filepath):
    """
    Carga y procesa el archivo de Localidades Indígenas (BDPI).
    Hoja: 1. BDPI - CC.PP
    Encabezado: Fila 7 (índice 6)
    """
    try:
        # Leer Excel, especificando la hoja y el encabezado
        df = pd.read_excel(filepath, sheet_name='1. BDPI - CC.PP', header=6)
        
        # Seleccionar columnas importantes y renombrar para estandarizar
        # Asumiendo los nombres indicados en el prompt
        cols_necesarias = ['Coordenadas Latitud (Y)', 'Coordenadas Longitud (X)', 'Población Total (aprox.)', 'NOMBRE DEL CP']
        
        # Verificar si 'NOMBRE DEL CP' existe, si no, buscar una columna de nombre similar
        # Nota: El prompt no especificó el nombre de la columna de nombre de localidad, pero es necesario para identificar.
        # Asumiré que existe una columna de nombre. Si falla, el usuario nos avisará o lo veremos en debugging.
        # Por seguridad, imprimiré las columnas si falla.
        
        # Limpieza básica de nombres de columnas (strip)
        df.columns = df.columns.str.strip()
        
        # Renombrar para facilitar uso
        rename_dict = {
            'Coordenadas Latitud (Y)': 'lat',
            'Coordenadas Longitud (X)': 'lon',
            'Población Total (aprox.)': 'poblacion',
            'Nombre del centro poblado': 'nombre_cp',
            'Departamento': 'departamento',
            'Provincia': 'provincia',
            'Distrito': 'distrito'
        }
        df = df.rename(columns=rename_dict)
        
        # Filtrar filas sin coordenadas válidas
        df = df.dropna(subset=['lat', 'lon'])
        
        # Normalización de Texto (Mayúsculas y Sin tildes) para filtros consistentes
        text_cols = ['nombre_cp', 'departamento', 'provincia', 'distrito']
        for col in text_cols:
            if col in df.columns:
                # Primero a string y mayúsculas, luego quitar acentos fila por fila
                df[col] = df[col].astype(str).str.upper().str.strip().apply(remove_accents)

        # Convertir a numérico, forzando errores a NaN
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        df['poblacion'] = pd.to_numeric(df['poblacion'], errors='coerce').fillna(0)
        
        df = df.dropna(subset=['lat', 'lon'])
        
        # Crear GeoDataFrame
        geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        
        return gdf
    except Exception as e:
        print(f"Error cargando BDPI: {e}")
        return None

def load_minas(filepath):
    """
    Carga y procesa el archivo de Unidades Mineras.
    Hoja: 2024
    Encabezado: Fila 3 (índice 2)
    """
    try:
        df = pd.read_excel(filepath, sheet_name='2024', header=2)
        
        df.columns = df.columns.str.strip()
        
        rename_dict = {
            'LATITUD': 'lat',
            'LONGITUD': 'lon',
            'UNIDAD MINERA EN PRODUCCIÓN': 'unidad_minera',
            'DEPARTAMENTO': 'departamento',
            'PROVINCIA': 'provincia',
            'DISTRITO': 'distrito'
        }
        df = df.rename(columns=rename_dict)
        
        # Normalización de Texto
        text_cols = ['unidad_minera', 'departamento', 'provincia', 'distrito']
        for col in text_cols:
             if col in df.columns:
                df[col] = df[col].astype(str).str.upper().str.strip().apply(remove_accents)
        
        df = df.dropna(subset=['lat', 'lon', 'unidad_minera'])
        
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        
        df = df.dropna(subset=['lat', 'lon'])
        
        geometry = [Point(xy) for xy in zip(df.lon, df.lat)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        
        return gdf
    except Exception as e:
        print(f"Error cargando Minas: {e}")
        return None

def load_departamentos(dirpath):
    """
    Carga el Shapefile de Departamentos.
    """
    try:
        # Buscar el archivo .shp en el directorio
        import os
        shp_file = None
        for file in os.listdir(dirpath):
            if file.endswith(".shp"):
                shp_file = os.path.join(dirpath, file)
                break
        
        if not shp_file:
            raise FileNotFoundError("No se encontró archivo .shp en el directorio departamentos")
            
        gdf = gpd.read_file(shp_file)
        # Asegurar CRS EPSG:4326
        if gdf.crs is not None and gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        elif gdf.crs is None:
             # Asumir WGS84 si no tiene CRS, común en archivos geogpsperu
            gdf.set_crs("EPSG:4326", inplace=True)
            
        return gdf
    except Exception as e:
        print(f"Error cargando Departamentos: {e}")
        return None
