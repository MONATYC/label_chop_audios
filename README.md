# Herramienta de Etiquetado y Corte de Audios

Este proyecto proporciona una interfaz gráfica (GUI) para etiquetar y cortar archivos de audio en segmentos categorizados. Está desarrollado con **PyQt6** y utiliza `librosa` y `matplotlib` para mostrar espectrogramas mientras se reproduce el audio.

## Requisitos

- Python 3.10 o superior
- [PyQt6](https://pypi.org/project/PyQt6/)
- [librosa](https://pypi.org/project/librosa/)
- [sounddevice](https://pypi.org/project/sounddevice/)
- [soundfile](https://pypi.org/project/soundfile/)
- [numpy](https://pypi.org/project/numpy/)
- [matplotlib](https://pypi.org/project/matplotlib/)

Instalación recomendada en un entorno virtual:

```cmd
python -m venv env
env\Scripts\activate
pip install PyQt6 librosa sounddevice soundfile numpy matplotlib
```

## Estructura del Proyecto

- `audio_labeling_project/`
  - `main.py`: Script principal para lanzar la aplicación.
  - `config.py`: Configuración de extensiones, categorías y rutas.
  - `audio_processor/`
    - `cutter.py`: Funciones para cortar segmentos de audio.
    - `spectrogram_generator.py`: Generación y anotación de espectrogramas.
  - `ui/`
    - `main_window.py`: Lógica de la ventana principal y controles de la GUI.
  - `utils/`
    - `file_manager.py`: Gestión de archivos y carpetas.
    - `logger.py`: Registro de audios ya etiquetados.
- `memlog/`
  - `log.json`: Registro de los audios ya procesados.

## Uso

Ejecuta la aplicación desde la raíz del repositorio:

```cmd
python audio_labeling_project/main.py
```

### Funcionalidades principales

- Selección de carpeta con archivos `.wav` o `.mp3`.
- Visualización del espectrograma del audio actual.
- Reproducción, pausa y parada del audio.
- Navegación entre archivos de audio.
- Modo de etiquetado: permite seleccionar segmentos en el espectrograma y asignarles una categoría.
- Guardado de los segmentos etiquetados como archivos individuales en la carpeta `labeled_cuts/`, organizados por categoría.
- Registro automático de los audios ya etiquetados para evitar reprocesarlos.
- Visualización de metadatos del archivo cargado (frecuencia de muestreo,
  duración y tamaño).
- Confirmación visual breve tras guardar los cortes.
- Atajos de teclado configurables para reproducir/pausar, marcar inicio,
  marcar fin y avanzar al siguiente audio.

### Categorías disponibles

Las categorías configuradas actualmente son:
- Hoot
- Climax
- Other_chimp
- No_chimp
- Human_presence
- Drumming

### Notas adicionales

- El sistema guarda un registro en `memlog/log.json` para no repetir el etiquetado de los mismos archivos.
- El espectrograma permite seleccionar regiones con el ratón en modo etiquetado.
- Los cortes se guardan automáticamente en subcarpetas según la categoría seleccionada.

