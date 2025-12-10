
import os
from pypdf import PdfReader
import re
import tkinter as tk
from tkinter import filedialog

def get_input_target_simple():
    """Abre un diálogo para seleccionar PDF o TXT."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Selecciona el documento para generar el examen",
        filetypes=[("Documentos", "*.pdf *.txt")]
    )
    return file_path

def clean_text_basic(text):
    """Limpieza básica: elimina espacios extra y líneas vacías."""
    # Eliminar caracteres no imprimibles o extraños si fuera necesario
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_text_from_pdf(pdf_path):
    """Extrae texto crudo de un PDF."""
    try:
        reader = PdfReader(pdf_path)
        full_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text.append(t)
        return "\n".join(full_text)
    except Exception as e:
        print(f"Error leyendo PDF {pdf_path}: {e}")
        return ""

def load_document(path):
    """Carga el contenido de un archivo (PDF o TXT) y devuelve string."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe: {path}")
    
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return load_text_from_pdf(path)
    elif ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        print(f"Formato no soportado: {ext}")
        return ""

def chunk_text(text, chunk_size=2000, overlap=200):
    """
    Divide el texto en bloques de aproximadamente 'chunk_size' caracteres.
    'overlap' asegura que no se corte contexto importante entre bloques.
    """
    text = clean_text_basic(text)
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        # Si no es el final, intentar cortar en un punto y seguido o espacio
        if end < text_len:
            # Buscar el último punto en el rango para cortar bien
            # Buscamos en los últimos 100 caracteres del chunk ideal
            search_window = text[end-100:end] 
            last_period = search_window.rfind('.')
            
            if last_period != -1:
                # Ajustar el final al periodo encontrado
                end = (end - 100) + last_period + 1
            else:
                # Si no hay punto, buscar espacio
                last_space = search_window.rfind(' ')
                if last_space != -1:
                    end = (end - 100) + last_space
        
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Avanzar el inicio, pero retrocediendo el overlap
        start = end - overlap
        
        # Seguridad para evitar bucles infinitos si overlap >= chunk_size
        if start >= end:
            start = end
            
    return chunks

if __name__ == "__main__":
    # Prueba rápida
    test_path = "Compendio.pdf"
    if os.path.exists(test_path):
        print("Cargando documento...")
        content = load_document(test_path)
        print(f"Longitud total: {len(content)} caracteres")
        
        chunks = chunk_text(content)
        print(f"Generados {len(chunks)} fragmentos.")
        print(f"Ejemplo Fragmento 1:\n{chunks[0][:200]}...")
