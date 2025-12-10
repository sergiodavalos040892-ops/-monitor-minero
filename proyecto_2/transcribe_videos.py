import traceback
import sys
import os
import whisper
import glob
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

def get_input_target():
    """Obtiene archivo o carpeta de entrada desde argumentos o GUI"""
    # 1. Drag & Drop (Argumentos)
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.exists(path):
            return path
    
    # 2. Selección Manual (GUI)
    print("Seleccionando entrada...")
    root = tk.Tk()
    root.withdraw() # Ocultar ventana principal
    
    # Preguntar al usuario qué desea seleccionar
    es_carpeta = messagebox.askyesno(
        "Tipo de Selección", 
        "¿Deseas transcribir una CARPETA completa?\n\nSí = Seleccionar Carpeta\nNo = Seleccionar un solo Archivo"
    )
    
    if es_carpeta:
        return filedialog.askdirectory(title="Selecciona la carpeta con archivos multimedia")
    else:
        return filedialog.askopenfilename(title="Selecciona el archivo de audio/video")

def transcribe_videos():
    target_path = get_input_target()
    
    if not target_path or not os.path.exists(target_path):
        print("No se seleccionó ninguna ruta válida.")
        return

    # Lista ampliada de extensiones (Video + Audio)
    # Nota: Usamos set para búsqueda rápida y lista para glob
    valid_extensions = {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".wma"}
    model_size = "base"
    
    # Forzar salida inmediata
    sys.stdout.reconfigure(encoding='utf-8')

    print(f"Cargando modelo Whisper '{model_size}'...")
    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"Error cargando el modelo: {e}")
        traceback.print_exc()
        return

    files_to_process = []

    # Lógica para Archivo Único vs Carpeta
    if os.path.isfile(target_path):
        # Caso: Archivo único
        path_obj = Path(target_path)
        if path_obj.suffix.lower() in valid_extensions:
            files_to_process.append(target_path)
        else:
            print(f"Advertencia: El archivo '{path_obj.name}' tiene una extensión no común ({path_obj.suffix}), pero intentaremos procesarlo.")
            files_to_process.append(target_path)
    else:
        # Caso: Carpeta
        print(f"Escaneando carpeta: {target_path}")
        for ext in valid_extensions:
            # glob pattern example: C:/path/*.mp4
            pattern = os.path.join(target_path, f"*{ext}")
            files_to_process.extend(glob.glob(pattern))

    if not files_to_process:
        print("No se encontraron archivos multimedia compatibles.")
        return

    print(f"Se encontraron {len(files_to_process)} archivos para procesar.")

    for video_path in files_to_process:
        try:
            # Construir nombre de archivo de salida
            path_obj = Path(video_path)
            output_filename = path_obj.stem + ".txt"
            output_path = path_obj.parent / output_filename
            
            if output_path.exists():
                print(f"Saltando {path_obj.name} - La transcripción ya existe.")
                continue

            print(f"Transcribiendo: {path_obj.name} ...")
            
            # Transcribir con progreso visible
            result = model.transcribe(video_path, verbose=True)
            text = result["text"]
            
            # Guardar
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text.strip())
            
            print(f"Guardado en: {output_filename}")
            
        except Exception as e:
            print(f"Error procesando {video_path}: {e}")
            traceback.print_exc()

    print("Proceso completado.")

if __name__ == "__main__":
    transcribe_videos()
