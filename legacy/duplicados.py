
import pandas as pd

# ===== CONFIGURACIÓN =====
# Columna por la que se hará la comparación
COLUMNA_COMUN = "id"  # 👈 cámbiala por la que quieras

# Archivos de entrada (pueden ser .csv o .xlsx)
ARCHIVO_1 = "archivo1.csv"
ARCHIVO_2 = "archivo2.csv"

# Archivos de salida
SALIDA_CON_DUP = "unificado_con_duplicados.csv"
SALIDA_SIN_DUP = "unificado_sin_duplicados.csv"


# ===== LECTURA DE ARCHIVOS =====
def leer_archivo(ruta):
    """Lee CSV o Excel automáticamente."""
    if ruta.endswith(".csv"):
        return pd.read_csv(ruta)
    elif ruta.endswith(".xlsx") or ruta.endswith(".xls"):
        return pd.read_excel(ruta)
    else:
        raise ValueError(f"Formato no soportado: {ruta}")


df1 = leer_archivo(ARCHIVO_1)
df2 = leer_archivo(ARCHIVO_2)

# ===== UNIFICAR Y COMPARAR =====
unificado = pd.concat([df1, df2], ignore_index=True)

# Guardar versión con duplicados
unificado.to_csv(SALIDA_CON_DUP, index=False)

# Eliminar duplicados en la columna elegida
sin_duplicados = unificado.drop_duplicates(subset=[COLUMNA_COMUN], keep="first")

# Guardar versión sin duplicados
sin_duplicados.to_csv(SALIDA_SIN_DUP, index=False)

print("✅ Archivos generados correctamente:")
print(f"- {SALIDA_CON_DUP}")
print(f"- {SALIDA_SIN_DUP}")
