# -*- coding: utf-8 -*-

import pandas as pd
import google.generativeai as genai
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

# --- CONFIGURACIÓN INICIAL ---
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("Error: No se encontró la GOOGLE_API_KEY.")
    print("Asegúrate de que tu archivo .env está en la misma carpeta y tiene el formato correcto.")
    exit()

# Configura el modelo de Gemini
model = genai.GenerativeModel('models/gemini-2.5-flash')

# --- CONFIGURACIONES DE ARCHIVO ---
ARCHIVO_ENTRADA = 'bibliografia Unida.xlsx'
ARCHIVO_SALIDA = 'bibliografia_filtrada_final.xlsx'

# 🔹 Nombre de la hoja a procesar (solo una)
HOJA_OBJETIVO = 'AI in Oncology'   # 👈 cámbiala según necesites

# 🔹 Columnas relevantes
COLUMNA_TITULO = 'Article Title'
COLUMNA_ABSTRACT = 'Abstract'       # 👈 nueva columna incluida

# --- ⚙️ CONFIGURACIÓN DE PRUEBA GLOBAL ---
MODO_PRUEBA = True
N_FILAS_PRUEBA = 9

# --- EL CEREBRO DEL FILTRO: EL PROMPT ---
def crear_prompt(titulo_del_paper, abstract_del_paper, nombre_de_la_hoja):
    return f"""
        Eres un asistente de investigación experto en inteligencia artificial aplicada a la Oncología de Precisión (Precision Oncology). 
        Tu tarea es clasificar un paper científico con base en su título y resumen (abstract).

        **Contexto de mi investigación:** Busco papers sobre el uso de **inteligencia artificial (IA)** —incluyendo *deep learning*, *machine learning*, 
        *redes neuronales*, *aprendizaje federado* u otros métodos de IA— aplicados a la **Oncología de Precisión**, 
        con énfasis en el **diagnóstico, pronóstico o recomendación de tratamientos personalizados en cáncer**, 
        especialmente en **cáncer de colon, pulmón o mama**.

        **Contexto:** Este paper proviene de la sección: **'{nombre_de_la_hoja}'**. 
        Usa esta pista junto con el título y abstract para decidir la relevancia.

        **Criterios de Relevancia (Sé estricto):**
        1. Debe mencionar o implicar el uso de **inteligencia artificial o aprendizaje automático** 
           (*machine learning*, *deep learning*, *AI*, *neural network*, *federated learning*, etc.).
        2. Debe estar **relacionado con Oncología de Precisión** o **tratamientos personalizados en cáncer**, 
           preferiblemente en **cáncer de colon, pulmón o mama**.

        **Instrucciones de Respuesta:**
        - Si cumple **AMBOS** criterios, responde solo **'SÍ'**.
        - Si no los cumple, responde solo **'NO'**.

        **Título:** "{titulo_del_paper}"
        **Abstract:** "{abstract_del_paper if isinstance(abstract_del_paper, str) else ''}"
    """

# --- FUNCIÓN PARA CLASIFICAR CON GEMINI ---
def es_relevante(titulo, abstract, nombre_de_la_hoja):
    if not isinstance(titulo, str) or not titulo.strip():
        return False

    prompt = crear_prompt(titulo, abstract, nombre_de_la_hoja)
    try:
        respuesta = model.generate_content(prompt)
        texto_limpio = respuesta.text.strip().upper()
        return texto_limpio == 'SÍ'
    except Exception as e:
        print(f"\nError al procesar el título '{titulo}': {e}")
        time.sleep(5)
        return False

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print(f"Cargando hoja '{HOJA_OBJETIVO}' del archivo: {ARCHIVO_ENTRADA}")
    try:
        df = pd.read_excel(ARCHIVO_ENTRADA, sheet_name=HOJA_OBJETIVO)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ARCHIVO_ENTRADA}'.")
        exit()
    except ValueError:
        print(f"Error: No se encontró la hoja '{HOJA_OBJETIVO}' en el archivo.")
        exit()

    print(f"--- Procesando hoja: '{HOJA_OBJETIVO}' ({len(df)} registros) ---")

    # Verifica columnas
    for col in [COLUMNA_TITULO, COLUMNA_ABSTRACT]:
        if col not in df.columns:
            print(f"Advertencia: La columna '{col}' no se encuentra en la hoja '{HOJA_OBJETIVO}'. Se omitirá.")
    
    # ⚙️ Modo de prueba
    if MODO_PRUEBA:
        df = df.head(N_FILAS_PRUEBA)
        print(f"⚠️ MODO PRUEBA ACTIVADO: Solo se procesarán las primeras {N_FILAS_PRUEBA} filas.")

    tqdm.pandas(desc=f"Filtrando '{HOJA_OBJETIVO}'")
    df['relevante'] = df.progress_apply(
        lambda fila: es_relevante(
            fila.get(COLUMNA_TITULO, ''),
            fila.get(COLUMNA_ABSTRACT, ''),
            HOJA_OBJETIVO
        ),
        axis=1
    )

    df_filtrado = df[df['relevante'] == True].copy()
    df_filtrado.drop(columns=['relevante'], inplace=True)

    print(f"Se encontraron {len(df_filtrado)} papers relevantes en '{HOJA_OBJETIVO}'.")

    df_filtrado.to_excel(ARCHIVO_SALIDA, sheet_name=HOJA_OBJETIVO, index=False)
    print(f"\n¡Proceso completado! Los resultados han sido guardados en '{ARCHIVO_SALIDA}'. uwu")
