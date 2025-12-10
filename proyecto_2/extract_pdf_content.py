
from pypdf import PdfReader
import re

def extract_clean_text(pdf_path, output_txt_path):
    print(f"Procesando: {pdf_path}")
    reader = PdfReader(pdf_path)
    full_text = []
    
    total_pages = len(reader.pages)
    print(f"Total de páginas: {total_pages}")

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        if text:
            # Limpieza básica por página
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                # 1. Eliminar espacios en blanco extremos
                line = line.strip()
                
                # 2. Saltar líneas que son solo números (números de página)
                if line.isdigit():
                    continue
                
                # 3. Saltar líneas muy cortas (ruido, letras sueltas) - ej: menos de 3 caracteres
                if len(line) < 4:
                    continue
                
                cleaned_lines.append(line)
            
            # Unir líneas limpias
            page_content = "\n".join(cleaned_lines)
            full_text.append(page_content)
        
        if (i + 1) % 50 == 0:
            print(f"Procesado {i + 1}/{total_pages} páginas...")

    # Guardar todo en un solo txt
    final_content = "\n\n".join(full_text)
    
    # Limpieza final: eliminar múltiples saltos de línea
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    
    print(f"¡Listo! Texto extraído guardado en: {output_txt_path}")

if __name__ == "__main__":
    pdf_file = "Compendio.pdf" # Nombre en el directorio local
    txt_file = "Compendio_LIMPIO.txt"
    extract_clean_text(pdf_file, txt_file)
