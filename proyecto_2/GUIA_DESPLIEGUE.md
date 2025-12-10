# Guía de Despliegue - Proyecto 2

Sigue estos pasos para poner tu aplicación en línea utilizando **Streamlit Community Cloud**. Es un servicio gratuito y fácil de usar.

## Paso 1: Preparar los Archivos
He asegurado que tengas todos los archivos necesarios en la carpeta `proyecto_2`:
- `app.py`: Tu aplicación principal.
- `requirements.txt`: Lista de librerías de Python.
- `packages.txt`: Librerías del sistema (necesarias para mapas).
- `.streamlit/config.toml`: Tu configuración de colores personalizada.
- `data/`: Tus archivos excel y mapas.

## Paso 2: Subir a GitHub
Streamlit Cloud lee el código directamente desde GitHub.

1. **Crea una cuenta en GitHub** si no tienes una: [github.com](https://github.com/).
2. **Crea un nuevo repositorio**:
   - Ve a [github.com/new](https://github.com/new).
   - Ponle un nombre, ej: `monitor-minero`.
   - Selecciona "Public".
   - Haz clic en "Create repository".
3. **Sube tus archivos**:
   - En la pantalla de tu nuevo repositorio, haz clic en el enlace **"uploading an existing file"**.
   - Arrastra **todo el contenido** de la carpeta `proyecto_2` a la página web.
     - *Importante*: Arrastra los archivos y carpetas que están DENTRO de `proyecto_2`, no la carpeta `proyecto_2` en sí misma. Deberías ver `app.py` en la raíz de la lista de subida.
   - Espera a que carguen todos los archivos.
   - Abajo, en "Commit changes", escribe "Versión inicial" y haz clic en el botón verde **"Commit changes"**.

## Paso 3: Desplegar en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io/).
2. Inicia sesión con tu cuenta de GitHub ("Continue with GitHub").
3. Haz clic en el botón azul **"New app"** (o "Deploy your first app").
4. Rellena el formulario:
   - **Repository**: Selecciona el repositorio que creaste (ej. `tu-usuario/monitor-minero`).
   - **Branch**: Déjalo en `main` (o `master`).
   - **Main file path**: Verifica que diga `app.py`.
5. Haz clic en **"Deploy!"**.

## Paso 4: ¡Listo!
- Streamlit comenzará a construir tu aplicación. Verás una terminal negra a la derecha con el progreso.
- Puede tardar unos minutos en instalar todo (especialmente GeoPandas).
- Una vez termine, tu app se abrirá automáticamente y te darán una URL (ej. `https://monitor-minero.streamlit.app`) que puedes compartir con cualquiera.

---
**Nota sobre Privacidad**: Al usar Streamlit Community Cloud gratuito, tu repositorio de GitHub debe ser público, lo que significa que cualquiera puede ver tu código y datos. Si tus datos son confidenciales, considera no subirlos o usar una versión privada.
