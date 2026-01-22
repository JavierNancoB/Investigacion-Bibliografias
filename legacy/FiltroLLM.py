# -*- coding: utf-8 -*-

import pandas as pd
import requests
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

# --- CONFIGURACIÓN INICIAL ---
OLLAMA_SERVER = os.environ.get("OLLAMA_SERVER", "http://127.0.0.1:11434")
MODEL_LOCAL = "deepseek-r1:1.5b"

# --- CONFIGURACIONES DE ARCHIVO ---
ARCHIVO_ENTRADA = 'doi_presentes_en_ambos.xlsx'
ARCHIVO_SALIDA = 'bibliografia_filtrada_final2.xlsx'

# Nombre de la hoja a procesar
HOJA_OBJETIVO = 'Ai Recomendations'

# Columnas relevantes
COLUMNA_TITULO = 'Title'
COLUMNA_ABSTRACT = 'Abstract'

# Configuración de prueba
MODO_PRUEBA = False
N_FILAS_PRUEBA = 20

# --- PROMPT EN INGLÉS ---
def crear_prompt(titulo_del_paper, abstract_del_paper, nombre_de_la_hoja):
    abstract_text = (abstract_del_paper[:500] + "...") if isinstance(abstract_del_paper, str) else ""
    return f"""
You are an expert research assistant specialized in artificial intelligence applied to Precision Oncology.
Classify the following paper based on its title and abstract.

Title: {titulo_del_paper}
Abstract: {abstract_text}
Source Section: {nombre_de_la_hoja}

Respond ONLY with YES or NO if the paper uses AI in Precision Oncology.
"""

# --- FUNCIÓN PARA CONSULTAR GEMMA3 LOCALMENTE ---
def es_relevante(titulo, abstract, nombre_de_la_hoja):
    if not isinstance(titulo, str) or not titulo.strip():
        print("⚠️ Empty title, automatically NO")
        return False

    prompt = crear_prompt(titulo, abstract, nombre_de_la_hoja)

    # Log del prompt (solo primeros 500 chars para no saturar)
    print("\n--- PROMPT ---")
    print(prompt[:500] + ('...' if len(prompt) > 500 else ''))
    print("--- END PROMPT ---\n")

    try:
        response = requests.post(
            f"{OLLAMA_SERVER}/v1/completions",
            json={
                "model": MODEL_LOCAL,
                "prompt": prompt
            },
            timeout=30
        )
        response.raise_for_status()
        resultado = response.json()

        # Extraemos la respuesta del modelo
        texto_limpio = resultado.get("completion", "")
        if not texto_limpio and resultado.get("choices"):
            texto_limpio = resultado['choices'][0].get('text', '')

        texto_limpio = texto_limpio.strip().upper()
        if not texto_limpio:
            print("⚠️ Model returned empty response, marking as NO by default")
            return False

        # Log de respuesta
        print(f"Title: {titulo[:60]}...")
        print(f"Model raw response: '{resultado}'")
        print(f"Cleaned response: '{texto_limpio}'")

        relevante = 'YES' in texto_limpio
        print(f"➡️ Classified as: {'YES' if relevante else 'NO'}\n")
        return relevante

    except Exception as e:
        print(f"\n❌ Error processing title '{titulo}': {e}")
        time.sleep(5)
        return False

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print(f"Loading sheet '{HOJA_OBJETIVO}' from file: {ARCHIVO_ENTRADA}")
    try:
        df = pd.read_excel(ARCHIVO_ENTRADA, sheet_name=HOJA_OBJETIVO)
    except FileNotFoundError:
        print(f"Error: File '{ARCHIVO_ENTRADA}' not found.")
        exit()
    except ValueError:
        print(f"Error: Sheet '{HOJA_OBJETIVO}' not found in the file.")
        exit()

    print(f"--- Processing sheet: '{HOJA_OBJETIVO}' ({len(df)} records) ---")

    # Verifica columnas
    for col in [COLUMNA_TITULO, COLUMNA_ABSTRACT]:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found in sheet '{HOJA_OBJETIVO}'. It will be skipped.")

    # ⚙️ Modo de prueba
    if MODO_PRUEBA:
        df = df.head(N_FILAS_PRUEBA)
        print(f"⚠️ TEST MODE ON: Only processing first {N_FILAS_PRUEBA} rows.")

    tqdm.pandas(desc=f"Filtering '{HOJA_OBJETIVO}'")
    df['relevant'] = df.progress_apply(
        lambda row: 'YES' if es_relevante(
            row.get(COLUMNA_TITULO, ''),
            row.get(COLUMNA_ABSTRACT, ''),
            HOJA_OBJETIVO
        ) else 'NO',
        axis=1
    )

    if MODO_PRUEBA:
        # Imprime todos los papers con la columna YES/NO
        print("\n=== TEST MODE OUTPUT ===")
        print(df[[COLUMNA_TITULO, 'relevant']])
    else:
        # Filtra los relevantes y guarda
        df_filtered = df[df['relevant'] == 'YES'].copy()
        df_filtered.drop(columns=['relevant'], inplace=True)
        print(f"Found {len(df_filtered)} relevant papers in '{HOJA_OBJETIVO}'.")
        df_filtered.to_excel(ARCHIVO_SALIDA, sheet_name=HOJA_OBJETIVO, index=False)
        print(f"\nProcess completed! Results saved in '{ARCHIVO_SALIDA}'. uwu")
