# Clasificador de Papers de IA en Oncología de Precisión

## Integrantes

* Aranza Sue Diaz
* Ignacio baeza
* Javier Nanco

Este proyecto es un **script en Python** para filtrar papers científicos desde un Excel, usando **Google Gemini**. Evalúa tanto **títulos** como **abstracts** y clasifica los papers como **relevantes** o no según criterios de IA aplicada a la Oncología de Precisión.

## Características

* Procesa una **hoja específica** del Excel (`HOJA_OBJETIVO`).
* Incluye **título y abstract** en la clasificación.
* **Modo de prueba** opcional (`MODO_PRUEBA`) para procesar solo unas filas.
* Genera un nuevo Excel con los papers filtrados.

## Configuración

1. Crear un archivo `.env` con tu `GOOGLE_API_KEY`.
2. Ajustar variables en el script:

   * `ARCHIVO_ENTRADA`, `ARCHIVO_SALIDA`
   * `HOJA_OBJETIVO`
   * `COLUMNA_TITULO`, `COLUMNA_ABSTRACT`
   * `MODO_PRUEBA` (`True` o `False`)

## Uso

```bash
python clasificador_papers.py
```

El script procesará la hoja seleccionada, clasificará cada paper y guardará los resultados en el Excel de salida.
