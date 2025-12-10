import pandas as pd
import os

BDPI_PATH = r"c:\Users\sergi\OneDrive\Documentos\ARTICULOS\proyecto 1\data\bdpi.xlsx"

try:
    df = pd.read_excel(BDPI_PATH, sheet_name='1. BDPI - CC.PP', header=6)
    print("Columnas encontradas:")
    for col in df.columns:
        print(f"'{col}'")
except Exception as e:
    print(e)
