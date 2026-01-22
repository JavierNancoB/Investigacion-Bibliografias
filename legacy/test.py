# -*- coding: utf-8 -*-
import requests
import os

# --- Configuración ---
OLLAMA_SERVER = os.environ.get("OLLAMA_SERVER", "http://127.0.0.1:11434")
MODEL_LOCAL = "deepseek-r1:1.5b"

# --- Función simple para probar ---
def es_relevante_simple(titulo, abstract):
    if not isinstance(titulo, str) or not titulo.strip():
        print("⚠️ Empty title, automatically NO")
        return "NO"

    prompt = f"""
Classify the following paper as YES or NO if it uses AI in Precision Oncology.

Title: {titulo}
Abstract: {abstract}

Respond ONLY with YES or NO.
"""

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

        # Usamos 'completion' si existe, si no fallback a choices
        texto_limpio = resultado.get("completion", "")
        if not texto_limpio and resultado.get("choices"):
            texto_limpio = resultado['choices'][0].get('text', '')

        texto_limpio = texto_limpio.strip().upper()
        print("=== RAW RESPONSE ===")
        print(resultado)
        print("\n=== CLEANED RESPONSE ===")
        print(texto_limpio)

        return "YES" if "YES" in texto_limpio else "NO"

    except Exception as e:
        print(f"❌ Error connecting to Gemma3: {e}")
        return "NO"


# --- Prueba ---
titulo = "Deep learning in cancer diagnosis"
abstract = "This paper applies AI methods to improve cancer detection."
resultado = es_relevante_simple(titulo, abstract)
print(f"\n➡️ Classified as: {resultado}")
