# -*- coding: utf-8 -*-
import pandas as pd
import google.generativeai as genai
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv
from multiprocessing import Pool, cpu_count
import numpy as np

# Carga las variables de entorno del archivo .env
load_dotenv()

# --- CONFIGURACIÓN DE ARCHIVO ---
ARCHIVO_ENTRADA = 'Bibliografia Unida.xlsx'
ARCHIVO_SALIDA = 'bibliografia_filtrada_final.xlsx'
HOJA_OBJETIVO = 'Precision Oncology'
COLUMNA_TITULO = 'Title'
COLUMNA_ABSTRACT = 'Abstract'

MODO_PRUEBA = False
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
def es_relevante(model, titulo, abstract, nombre_de_la_hoja):
    if not isinstance(titulo, str) or not titulo.strip():
        return False
    prompt = crear_prompt(titulo, abstract, nombre_de_la_hoja)
    try:
        respuesta = model.generate_content(prompt)
        texto_limpio = respuesta.text.strip().upper()
        return texto_limpio == 'SÍ'
    except Exception as e:
        print(f"Error con '{titulo[:40]}...': {e}")
        time.sleep(5)
        return False

# --- FUNCIÓN DE PROCESAMIENTO PARALELO ---
def procesar_parte(args):
    parte_df, api_key, hoja, idx = args

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')

    tqdm.pandas(desc=f"Parte {idx+1}")
    parte_df['relevante'] = parte_df.progress_apply(
        lambda fila: es_relevante(
            model,
            fila.get(COLUMNA_TITULO, ''),
            fila.get(COLUMNA_ABSTRACT, ''),
            hoja
        ),
        axis=1
    )

    df_filtrado = parte_df[parte_df['relevante'] == True].copy()
    temp_file = f"temp_result_{idx}.xlsx"
    df_filtrado.drop(columns=['relevante'], inplace=True)
    df_filtrado.to_excel(temp_file, index=False)
    return temp_file

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # Cargar todas las API keys numeradas
    api_keys = [v for k, v in os.environ.items() if k.startswith("GOOGLE_API_KEY")]
    api_keys = sorted(api_keys)  # ordenadas
    if not api_keys:
        print("❌ No se encontraron API keys en el .env")
        exit()

    print(f"🔑 Se encontraron {len(api_keys)} API keys disponibles.")
    print(f"Cargando hoja '{HOJA_OBJETIVO}' del archivo '{ARCHIVO_ENTRADA}'...")

    try:
        df = pd.read_excel(ARCHIVO_ENTRADA, sheet_name=HOJA_OBJETIVO)
    except Exception as e:
        print(f"Error al leer el Excel: {e}")
        exit()

    if MODO_PRUEBA:
        df = df.head(N_FILAS_PRUEBA)
        print(f"⚠️ MODO PRUEBA ACTIVADO ({N_FILAS_PRUEBA} filas).")

    n_partes = min(len(api_keys), len(df))
    partes = np.array_split(df, n_partes)

    print(f"Dividiendo en {n_partes} partes según las API keys disponibles...")

    args = [(partes[i], api_keys[i % len(api_keys)], HOJA_OBJETIVO, i) for i in range(n_partes)]

    with Pool(processes=min(len(api_keys), cpu_count())) as pool:
        archivos_temp = pool.map(procesar_parte, args)

    # Unir resultados
    print("🧩 Uniendo resultados...")
    dfs_finales = [pd.read_excel(f) for f in archivos_temp]
    df_final = pd.concat(dfs_finales, ignore_index=True)
    df_final.to_excel(ARCHIVO_SALIDA, sheet_name=HOJA_OBJETIVO, index=False)

    # Limpiar archivos temporales
    for f in archivos_temp:
        os.remove(f)

    print(f"✅ ¡Proceso completado! Resultados guardados en '{ARCHIVO_SALIDA}'.")
