
import ollama
import json
import re

# Configuración del Prompt Maestro
SYSTEM_PROMPT = """
Eres un profesor universitario experto y exigente. Tu tarea es evaluar la comprensión profunda de un texto.
Genera un cuestionario basado EXCLUSIVAMENTE en el texto proporcionado.

REGLAS:
1. Genera 3 preguntas de opción múltiple (Multiple Choice) difíciles.
2. Genera 1 pregunta de desarrollo (Open Ended) que requiera síntesis.
3. El formato de salida debe ser JSON puro, sin texto adicional.

FORMATO JSON ESPERADO:
{
  "multiple_choice": [
    {
      "question": "¿Pregunta 1?",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "B",
      "explanation": "Explicación breve de por qué es la correcta."
    },
    ...
  ],
  "open_ended": {
    "question": "¿Pregunta de desarrollo?",
    "key_points": ["Punto clave 1", "Punto clave 2"]
  }
}
"""

def generate_questions_from_chunk(chunk_text, model="llama3"):
    """
    Envía un fragmento de texto a Ollama y retorna las preguntas generadas en formato dict.
    """
    user_message = f"TEXTO A EVALUAR:\n---\n{chunk_text}\n---\n\nGenera el cuestionario en JSON:"
    
    try:
        response = ollama.chat(model=model, messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_message},
        ], format='json') # Forzamos salida JSON nativa de Ollama si está soportada, o parseamos.
        
        content = response['message']['content']
        
        # Parsear JSON
        try:
            quiz_data = json.loads(content)
            
            # Basic Schema Validation
            if not isinstance(quiz_data, dict):
                return None
            if 'multiple_choice' in quiz_data and not isinstance(quiz_data['multiple_choice'], list):
                # Try to fix scalar value or discard
                quiz_data['multiple_choice'] = []
            
            return quiz_data
        except json.JSONDecodeError:
            # Fallback simple si el modelo añade texto extra
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                print(f"Error parseando JSON de Ollama. Respuesta cruda: {content[:100]}...")
                return None
                
    except Exception as e:
        print(f"Error comunicando con Ollama: {e}")
        return None

if __name__ == "__main__":
    # Test simple
    test_text = "El derecho administrativo es la rama del derecho público que regula la organización, funcionamiento, poderes y deberes de la Administración pública."
    print("Probando generación con texto de prueba...")
    result = generate_questions_from_chunk(test_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
