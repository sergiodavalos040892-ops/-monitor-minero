import pandas as pd
import os

MINAS_PATH = r"c:\Users\sergi\OneDrive\Documentos\ARTICULOS\proyecto 1\data\minas.xlsx"

try:
    df = pd.read_excel(MINAS_PATH, sheet_name='2024', header=2)
    print("Columnas Minas encontradas:")
    for col in df.columns:
        print(f"'{col}'")
except Exception as e:
    print(e)
