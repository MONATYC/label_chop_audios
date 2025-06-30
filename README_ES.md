# Herramienta de Etiquetado y Corte de Audios

Esta aplicación permite etiquetar segmentos de archivos de audio y guardar los cortes de manera organizada. Está pensada para flujos de trabajo de anotación de sonidos como llamadas de chimpancé u otras clasificaciones personalizadas.

## Características

- Interfaz gráfica construida con **PyQt6**.
- Reproducción de audio con control de posición y visualización de la forma de onda mediante espectrogramas.
- Modo de etiquetado que permite seleccionar regiones del espectrograma con el ratón.
- Almacena las anotaciones y genera archivos recortados por categoría en la carpeta `labeled_cuts/`.
- Registra los audios ya etiquetados para evitar procesarlos de nuevo.

## Instalación

1. Requiere Python 3.10 o superior. Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate
```

2. Instalar las dependencias principales:

```bash
pip install PyQt6 numpy sounddevice soundfile librosa matplotlib
```

## Uso

1. Ejecuta la aplicación:

```bash
python audio_labeling_project/main.py
```

2. Selecciona la carpeta que contiene los archivos de audio (`.wav` o `.mp3`).
3. Navega por los audios con los botones **Next** y **Previous**.
4. Activa **Label Mode** para marcar segmentos sobre el espectrograma. Cada selección se añadirá a la lista de anotaciones.
5. Pulsa **Save Labels & Cut** para guardar los cortes etiquetados en `labeled_cuts/` y registrar el audio como procesado.
6. En los controles de reproducción encontrarás los botones **Play/Pause** y **Stop**. *Play/Pause* detiene la reproducción en el punto actual para reanudarla desde allí, mientras que *Stop* vuelve al inicio del audio.

## Personalización

- Las categorías de etiqueta y otros parámetros se encuentran en `audio_labeling_project/config.py`.
- Los cortes guardados se organizan por categoría dentro de la carpeta del audio original.

## Estructura del proyecto

```
 audio_labeling_project/
 ├── audio_processor/       # Funciones para cortar audio y generar espectrogramas
 ├── ui/                    # Ventanas y widgets de la interfaz PyQt6
 ├── utils/                 # Utilidades de gestión de archivos y registro
 ├── config.py              # Ajustes generales (extensiones, categorías, etc.)
 └── main.py                # Punto de entrada de la aplicación
```

## Contribución

Las mejoras y correcciones son bienvenidas. Abre un *issue* o envía un *pull request* describiendo tu propuesta.

