@echo off
chcp 65001 > nul
echo ===================================================
echo   TRANSCRIBIR VIDEOS (IA) - NVIDIA GPU DETECTED
echo ===================================================
echo.
echo Arrastra una carpeta aqui para empezar...
echo O presiona ENTER para abrir el selector de carpetas.
echo.

:: Ejecutar el script python pasando cualquier argumento (como la carpeta arrastrada)
python "%~dp0transcribe_videos.py" %*

echo.
echo ===================================================
echo   Proceso finalizado.
echo ===================================================
pause
