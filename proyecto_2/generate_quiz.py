

import os
import sys
import json
import time
from tqdm import tqdm
import input_handler
import question_generator

def save_intermediate_progress(batch_data, recovery_file):
    """Guarda un lote de preguntas en un archivo JSONL (una línea por bloque)."""
    with open(recovery_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(batch_data, ensure_ascii=False) + "\n")

def load_recovery(recovery_file):
    """Carga el progreso previo si existe."""
    if not os.path.exists(recovery_file):
        return []
    
    recovered_data = []
    print(f"--> ¡Encontrado archivo de recuperación! {recovery_file}")
    try:
        with open(recovery_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    recovered_data.append(json.loads(line))
        print(f"--> Se recuperaron {len(recovered_data)} bloques ya procesados. Saltando...")
        return recovered_data
    except Exception as e:
        print(f"--> Error leyendo recuperación: {e}. Se empezará de cero.")
        return []

def save_to_html(quiz_data, output_filename, source_name):
    """Genera un archivo HTML interactivo con las preguntas, robusto a errores."""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Examen: {source_name}</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }}
            .quiz-container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .question-card {{ border-bottom: 1px solid #eee; padding: 20px 0; }}
            .question-text {{ font-size: 1.1em; font-weight: 600; color: #34495e; }}
            .options {{ margin-top: 10px; }}
            .option {{ display: block; margin: 5px 0; padding: 10px; background: #f8f9fa; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; transition: 0.2s; }}
            .option:hover {{ background: #e9ecef; }}
            .answer-key {{ display: none; margin-top: 10px; padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px; }}
            .show-btn {{ background-color: #007bff; color: white; border: none; padding: 5px 15px; border-radius: 4px; cursor: pointer; margin-top: 10px; font-size: 0.9em; }}
            .show-btn:hover {{ background-color: #0056b3; }}
            .open-question {{ background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            .error-card {{ background-color: #ffe6e6; padding: 10px; border: 1px solid #ffcccc; color: #cc0000; display: none; }}
        </style>
        <script>
            function toggleAnswer(id) {{
                var x = document.getElementById(id);
                if (x.style.display === "none") {{ x.style.display = "block"; }} else {{ x.style.display = "none"; }}
            }}
        </script>
    </head>
    <body>
        <div class="quiz-container">
            <h1>Examen Generado con IA</h1>
            <p>Fuente: <strong>{source_name}</strong></p>
            <hr>
    """
    
    count = 1
    for i, batch in enumerate(quiz_data):
        if not batch: continue
        
        # Multiple Choice
        if 'multiple_choice' in batch:
            for q in batch['multiple_choice']:
                # VALIDATION: Ensure q is a dictionary
                if not isinstance(q, dict):
                    continue

                # SAFETY CHECK: Si la IA alucinó y no puso 'options', saltamos o ponemos default
                options = q.get('options', [])
                if not options:
                    continue # Saltamos preguntas mal formadas
                
                q_id = f"q_{count}"
                options_html = ""
                for opt in options:
                    options_html += f"<label class='option'><input type='radio' name='{q_id}'> {opt}</label>"
                
                html_content += f"""
                <div class="question-card">
                    <div class="question-text">{count}. {q.get('question', 'Pregunta sin texto')}</div>
                    <div class="options">{options_html}</div>
                    <button class="show-btn" onclick="toggleAnswer('ans_{q_id}')">Ver Respuesta</button>
                    <div id="ans_{q_id}" class="answer-key">
                        <strong>Correcta:</strong> {q.get('answer', '?')}<br>
                        <em>{q.get('explanation', '')}</em>
                    </div>
                </div>
                """
                count += 1
        
        # Open Ended
        if 'open_ended' in batch:
            oq = batch.get('open_ended', {})
            if oq and 'question' in oq:
                html_content += f"""
                <div class="open-question">
                    <strong>Pregunta de Desarrollo {i+1}:</strong><br>
                    {oq.get('question', '')}
                    <br><br>
                    <details>
                        <summary>Ver Puntos Clave Sugeridos</summary>
                        <ul>
                            {''.join([f'<li>{p}</li>' for p in oq.get('key_points', [])])}
                        </ul>
                    </details>
                </div>
                """

    html_content += """
        </div>
    </body>
    </html>
    """
    
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"\n¡Examen guardado en HTML! -> {output_filename}")
        os.startfile(output_filename) # Abrir automáticamente
    except Exception as e:
        print(f"Error escribiendo archivo HTML: {e}")

def main():
    print("--- GENERADOR DE EXÁMENES PROFUNDOS (GPU) - MODO SEGURO ---")
    
    # 1. Obtener archivo
    target_path = input_handler.get_input_target_simple()
    if not target_path:
        # Fallback manual
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        target_path = filedialog.askopenfilename(title="Selecciona un PDF o TXT para estudiar")
        root.destroy()
    
    if not target_path or not os.path.exists(target_path):
        print("No se seleccionó archivo.")
        return

    # Archivo de recuperación basado en el nombre del input
    recovery_filename = f"{target_path}.recovery.jsonl"

    print(f"\n1. Cargando: {os.path.basename(target_path)}")
    text_content = input_handler.load_document(target_path)
    
    print("\n2. Segmentando documento (Estrategia de Barrido)...")
    chunks = input_handler.chunk_text(text_content, chunk_size=3000, overlap=300)
    total_chunks = len(chunks)
    print(f"-> Se generaron {total_chunks} bloques de estudio.")
    
    if total_chunks == 0:
        print("El documento parece vacío.")
        return

    # Cargar progreso previo
    all_quiz_data = load_recovery(recovery_filename)
    start_index = len(all_quiz_data)
    
    if start_index >= total_chunks:
        print("\n¡Parece que este documento ya fue procesado completamente!")
        print("Generando HTML directamente...")
    else:
        print(f"\n3. Generando preguntas con IA (Ollama/Llama3)...")
        print(f"   Retomando desde el bloque {start_index+1}/{total_chunks}")
        print("   (Las preguntas se guardan automáticamente por seguridad)\n")
        
        # Iterar desde donde nos quedamos
        for i in tqdm(range(start_index, total_chunks), unit="bloque"):
            chunk = chunks[i]
            quiz_batch = question_generator.generate_questions_from_chunk(chunk)
            
            # Aunque falle/venga vacío, lo guardamos (como None/Dict vacío) para avanzar el índice
            # y no quedarnos en bucle infinito en un bloque malo.
            if not quiz_batch:
                quiz_batch = {} 
            
            all_quiz_data.append(quiz_batch)
            save_intermediate_progress(quiz_batch, recovery_filename)
    
    print(f"\n4. Finalizado. Procesados {len(all_quiz_data)} bloques.")
    
    # Exportar
    output_filename = f"EXAMEN_{os.path.basename(target_path)}.html"
    save_to_html(all_quiz_data, output_filename, os.path.basename(target_path))
    
    # Opcional: Limpiar recovery si todo salió bien
    # os.remove(recovery_filename) 

if __name__ == "__main__":
    main()
