# Clasificador de Papers de IA en Oncología de Precisión

## Descripción General

Este proyecto implementa un **pipeline reproducible de integración, depuración, deduplicación y filtrado temático de literatura científica** orientada a **Inteligencia Artificial aplicada a Oncología de Precisión**.

El objetivo principal es construir un **corpus bibliográfico de alta calidad estructural y temática**, listo para ser validado semánticamente mediante modelos de lenguaje (LLMs) y utilizado en análisis posteriores (revisión sistemática asistida, priorización de evidencia, mapeo de tendencias, etc.).

El flujo de trabajo se divide en **tres etapas principales**, cada una con criterios explícitos, trazabilidad completa y justificación metodológica.

---

## Integrantes

* Aranza Sue Díaz
* Ignacio Baeza
* Javier Nanco

---

## Estructura del Proyecto

```
├── 01_Bibliometric_Data_Integration_and_Structural_Filtering.ipynb
├── /legacy
└── README.md
```

---

## Fuentes de Datos

El dataset inicial proviene de un archivo Excel con múltiples hojas, cada una correspondiente a consultas bibliográficas realizadas en distintas bases de datos (por ejemplo: IEEE, Springer, Google Scholar, PubMed, etc.).

Cada hoja es preservada mediante una columna de **trazabilidad (`source_sheet`)**, lo que permite identificar el origen exacto de cada registro durante todo el pipeline.

---

## Etapa 0 — Integración Bibliométrica y Normalización Estructural

### 1. Carga y Unificación de Fuentes

* Se cargan simultáneamente todas las hojas del archivo Excel.
* Se concatenan en un único DataFrame.
* Se añade la columna `source_sheet` para preservar el origen de cada registro.

### 2. Normalización de Metadatos

Dado el carácter heterogéneo de los esquemas bibliográficos, se construyen **campos canónicos normalizados** mediante coalescencia semántica:

| Campo Canónico  | Descripción                      |
| --------------- | -------------------------------- |
| `title_norm`    | Título del artículo              |
| `doi_norm`      | DOI normalizado                  |
| `year_norm`     | Año de publicación               |
| `authors_norm`  | Autores                          |
| `source_norm`   | Revista, conferencia o editorial |
| `type_norm`     | Tipo de documento                |
| `abstract_norm` | Resumen                          |
| `url_norm`      | Enlace al documento              |
| `keywords_norm` | Palabras clave                   |

Todos los campos textuales relevantes se normalizan a minúsculas y se limpian de ruido básico.

### 3. Evaluación de Completitud

Se calcula un **índice de completitud de metadatos** por registro (0–1), basado en la presencia de 7 campos clave.

**Resultados principales:**

* 100 % de los registros tienen título y DOI.
* > 99.8 % tienen año de publicación.
* ~77 % no poseen resumen (limitación esperable en bases técnicas).
* 97 % de los registros poseen al menos 5 de 7 metadatos canónicos.

**Conclusión:**
El corpus es estructuralmente robusto y óptimo para deduplicación y filtrado avanzado.

---

## Etapa 1 — Deduplicación y Filtrado Estructural

### 1. Deduplicación con Jerarquía y Trazabilidad

Se aplica una deduplicación **conservadora y jerárquica**:

1. **Duplicados por DOI** (clave fuerte).
2. **Duplicados por título** solo cuando no existe DOI diferenciador (clave débil).

Este enfoque evita falsos positivos y preserva versiones legítimamente distintas de una misma obra.

**Resultados:**

* Registros iniciales: 9.569
* Registros únicos tras deduplicación: 4.114
* Duplicados eliminados: 5.455

Cada eliminación queda documentada mediante la columna `dedup_reason`.

### 2. Filtrado Temporal y por Tipo de Documento

* Año mínimo: **2018**
* Tipos aceptados:

  * Article
  * Journal article
  * Conference paper
  * Research article

**Resultado final Etapa 1:**

* Registros conservados: **2.493**
* Exportado como: `bibliografia_etapa1.csv`

---

## Etapa 2 — Filtrado Temático y Scoring de Relevancia

### 1. Filtrado Temático Avanzado

Se construye un campo combinado (`text_combined`) a partir de:

* Título normalizado
* Resumen
* Palabras clave

#### Palabras clave obligatorias (al menos una):

* precision oncology
* deep learning
* federated learning
* breast cancer
* lung cancer

#### Palabras clave de exclusión:

* review
* case report
* editorial
* letter
* conference abstract
* animal model

**Resultado:**

* Antes del filtrado: 2.493 registros
* Después del filtrado: **634 registros**

---

### 2. Scoring de Relevancia Temática

Cada artículo recibe un **score cuantitativo de relevancia**, desglosado en tres dimensiones:

* **Técnica:** machine learning, AI, radiomics, multi-omics, etc.
* **Clínica:** biomarkers, treatment response, personalized medicine, clinical trial, etc.
* **Federada / distribuida:** privacy-preserving, multi-institutional, decentralized training, etc.

El `relevance_score` es la suma de los tres componentes:

```
relevance_score = technical_score + clinical_score + federated_score
```

Este score permite **priorizar artículos de alto valor antes de la validación semántica con LLMs**.

---

### 3. Exportación Final

El dataset final incluye:

* Metadatos originales y normalizados
* Campo de texto combinado
* Scores de relevancia (total y por dimensión)

Archivo generado:

```
/content/drive/MyDrive/Título/bibliografia_etapa2.csv
```

* Registros exportados: **634**

Adicionalmente, se establece como criterio final conservar únicamente artículos con **relevance_score > 4**, para maximizar pertinencia temática.

---

## Estado del Proyecto

* Integración y depuración bibliográfica: **Completa**
* Filtrado estructural y temático: **Completo**
* Scoring de relevancia: **Completo**
* Validación semántica con LLM (local): **Pendiente / Etapa siguiente**

---

## Uso Esperado

Este proyecto está diseñado para ser utilizado como:

* Preprocesamiento para revisiones sistemáticas asistidas por IA
* Construcción de corpora curados para análisis bibliométrico
* Entrada estructurada para evaluación semántica mediante LLMs
* Base para estudios de tendencias en IA aplicada a oncología de precisión
