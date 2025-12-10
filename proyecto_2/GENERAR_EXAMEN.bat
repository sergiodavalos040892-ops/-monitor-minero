@echo off
chcp 65001 > nul
echo ===================================================
echo   GENERADOR DE EXAMENES (IA LOCAL - OLLAMA)
echo ===================================================
echo.
echo Generando preguntas profundas basadadas en tu documento...
echo Esto usara tu GPU NVIDIA y el modelo Llama 3.
echo.

python "%~dp0generate_quiz.py" %*

echo.
echo ===================================================
echo   Cuestionario generado. Revisa el archivo HTML.
echo ===================================================
pause
