---
name: SKILL-ODP
description: Open Data Peru — Analisis metodologicamente correcto de ENAHO (INEI Peru). Genera codigo en Python, R y Stata con factores de expansion, llaves de merge correctas, y validacion. Activa con "usemos ODP", "analicemos ENAHO", o cuando el usuario trabaje con datos de encuestas de hogares del Peru.
license: MIT
metadata:
  skill-author: Donny Tapara
  version: "0.1"
---

# SKILL: OPEN DATA PERU (ODP)
> Encuesta Nacional de Hogares (ENAHO) — INEI Peru
> Version: 0.1 | Marzo 2025 | Open Source
> Autor: Donny Tapara

---

## Activacion

Esta skill se activa cuando el usuario:
- Dice "usemos ODP", "Open Data Peru", "analicemos ENAHO", o variantes
- Menciona analisis de datos INEI, ENAHO, encuestas de hogares Peru
- Tiene archivos .dta, .sav, .csv de ENAHO y necesita procesarlos
- Pregunta sobre pobreza, empleo, salud, educacion, gastos en Peru con datos oficiales

---

## Base de Datos de Metadatos (SQLite)

**REGLA CRITICA:** Antes de generar CUALQUIER codigo que referencie variables ENAHO, DEBES consultar la SQLite. Nunca asumir nombres de variables desde memoria.

**Ubicacion:** `metadata/enaho_variables.db` (relativa a esta skill)

Si la ruta relativa no funciona, buscar en:
1. El directorio de la skill instalada
2. Preguntar al usuario la ruta de la .db

### Consulta rapida (ejecutar via Bash con Python)

```python
import sqlite3
conn = sqlite3.connect("RUTA/enaho_variables.db")

# Listar modulos
conn.execute("SELECT codigo, nombre, nivel FROM modulos ORDER BY codigo").fetchall()

# Verificar variable
conn.execute("""
    SELECT v.nombre, v.etiqueta, v.tipo, m.codigo as modulo
    FROM variables v JOIN modulos m ON v.modulo_id = m.id
    WHERE v.nombre = ? AND v.anio = ?
""", ("NOMBRE_VAR", 2024)).fetchall()

# Buscar variables por patron
conn.execute("""
    SELECT v.nombre, v.etiqueta, m.codigo
    FROM variables v JOIN modulos m ON v.modulo_id = m.id
    WHERE v.nombre LIKE ? AND v.anio = ?
""", ("%PATRON%", 2024)).fetchall()

# Obtener nivel de un modulo
conn.execute("SELECT nivel FROM modulos WHERE codigo = ?", ("500",)).fetchone()

# Categorias de una variable
conn.execute("""
    SELECT c.valor, c.etiqueta, c.es_centinela
    FROM categorias c JOIN variables v ON c.variable_id = v.id
    WHERE v.nombre = ? AND v.anio = ?
""", ("P207", 2024)).fetchall()
```

---

## Flujo Conversacional

Cuando el usuario activa la skill, sigue este protocolo paso a paso. NO saltar pasos. Cada paso requiere interaccion.

### PASO 1: BIENVENIDA Y CONTEXTO

Presentarte como asistente especializado en ENAHO y preguntar:

1. **Objetivo de investigacion:** "Cual es tu pregunta de investigacion o que quieres analizar?"
   - Escuchar atentamente: temas como empleo, pobreza, salud, educacion, gastos, produccion agropecuaria, etc.
2. **Anio(s):** "Que anio(s) necesitas? Tenemos metadatos para 2015, 2020 y 2024."
   - Si quiere mas anios: la estructura es similar, pero verificar variables en SQLite
3. **Directorio:** "Donde tienes (o quieres) los archivos de ENAHO?"

### PASO 2: EVALUACION Y SUGERENCIA DE LENGUAJE

Evaluar el contexto del usuario para SUGERIR el lenguaje mas apropiado:

| Señal del usuario | Lenguaje sugerido | Razon |
|---|---|---|
| Menciona pandas, jupyter, ML, data science | **Python** | Ecosistema natural |
| Menciona srvyr, tidyverse, regresiones, publicacion academica | **R** | Mejor soporte survey y academico |
| Menciona dofiles, .dta, econometria tradicional, Stata | **Stata** | Flujo de trabajo habitual |
| Menciona Positron | **Python o R** | Ambos disponibles, preguntar preferencia |
| Sin señal clara | **Preguntar** | "Que software tienes instalado? Python, R, Stata?" |

Librerias especializadas por lenguaje:

| Lenguaje | Libreria | Instalacion | Rol |
|---|---|---|---|
| Python | `enahopy` | `pip install enahopy` | Descarga, carga ENAHO |
| R | `enaho` | `install.packages("enaho")` | Descarga, carga, panel |
| Stata | `enahodata` | `ssc install enahodata` | Descarga y descompresion |

**IMPORTANTE:** Si la libreria especializada no cubre la operacion necesaria, usar las herramientas base del lenguaje (pandas, haven/dplyr, comandos nativos Stata) pero SIEMPRE con las reglas metodologicas de esta skill.

### PASO 3: PROPUESTA DE MODULOS Y VARIABLES

Segun el objetivo del usuario:

1. **Consultar SQLite** para identificar modulos relevantes
2. **Verificar variables clave** para el objetivo en los anios solicitados
3. **Proponer:**
   - Modulos a usar (con codigos y nombres)
   - Unidad de analisis (persona o hogar) — ver `metodologia/unidades_analisis.md`
   - Variables sugeridas (verificadas en SQLite)
   - Factor de expansion correspondiente — ver `metodologia/factores_expansion.md`
4. **Si necesita datos provinciales/distritales:** ADVERTIR sobre representatividad y sugerir datos pooled — ver `metodologia/append_pooled.md`
5. **Si involucra ingresos o gastos monetarios:** preguntar si necesita deflactar — ver `metodologia/deflactores.md`

**>>> ESPERAR VALIDACION DEL USUARIO ANTES DE CONTINUAR <<<**

### PASO 4: GENERACION DE CODIGO

Generar codigo completo con esta estructura:

```
# ============================================================
# OPEN DATA PERU — [Titulo del analisis]
# Modulos: [lista]
# Anio(s): [lista]
# Unidad de analisis: [persona/hogar]
# Factor de expansion: [FACTOR07/FAC500A/etc.]
# Generado con ODP Skill v0.1
# ============================================================

# BLOQUE 1: Instalacion y carga de librerias
# BLOQUE 2: Descarga de modulos (si aplica)
# BLOQUE 3: Carga de datos
# BLOQUE 4: Normalizacion de variables (MAYUSCULAS)
# BLOQUE 5: Merge/Union de modulos
# BLOQUE 6: Seleccion de variables
# BLOQUE 7: Limpieza (centinelas, filtros)
# BLOQUE 8: Analisis con factor de expansion
# BLOQUE 9: Validacion post-merge
# BLOQUE 10: Reporte resumen
```

### PASO 5: VALIDACION Y REPORTE

Incluir al final del codigo generado:
- Verificacion de N (observaciones totales)
- Verificacion de duplicados en llaves de union
- Verificacion de factor de expansion (presente, positivo, rango razonable)
- Reporte de missings por variable (alertar si >10%)
- Resumen: modulos cargados, N, variables, advertencias

---

## Reglas de Merge Genericas

El merge entre modulos ENAHO se determina por el `nivel` de cada modulo en la SQLite.

### Regla fundamental

| Modulo A (nivel) | Modulo B (nivel) | Llaves de merge | Tipo |
|---|---|---|---|
| hogar | hogar | CONGLOME, VIVIENDA, HOGAR | 1:1 |
| persona | persona | CONGLOME, VIVIENDA, HOGAR, CODPERSO | 1:1 |
| persona | hogar | CONGLOME, VIVIENDA, HOGAR | m:1 |
| hogar | persona | CONGLOME, VIVIENDA, HOGAR | 1:m |

### Casos especiales

1. **Modulos de gastos (601-613):** Marcados como `hogar` pero pueden tener MULTIPLES filas por hogar (una por item/producto). Al hacer merge con otro modulo hogar (ej. 100), el resultado sera 1:m. **Siempre verificar duplicados post-merge.**

2. **Modulos agropecuarios (2000-2700):** Similar a gastos — nivel hogar pero posibles multiples filas por parcela/producto. Verificar estructura antes de merge.

3. **Sumarias (SUM8G, SUM12G):** Verdadero nivel hogar, una fila por hogar. Merge limpio con cualquier modulo hogar.

4. **Modulo 200 (Miembros del Hogar):** Nivel persona. Es el modulo base para merges a nivel persona — contiene CODPERSO.

### Merge en cadena

Para unir 3+ modulos, hacer merge secuencial:
```
Base (M200) → + M300 (persona 1:1) → + M500 (persona 1:1) → + M100 (m:1 a hogar)
```

El modulo con MAS filas debe ser la base del merge.

### Consulta SQLite para merge

```python
# Determinar llaves automaticamente
def get_merge_keys(conn, codigo_a, codigo_b):
    nivel_a = conn.execute("SELECT nivel FROM modulos WHERE codigo=?", (codigo_a,)).fetchone()[0]
    nivel_b = conn.execute("SELECT nivel FROM modulos WHERE codigo=?", (codigo_b,)).fetchone()[0]

    if nivel_a == 'persona' or nivel_b == 'persona':
        if nivel_a == 'persona' and nivel_b == 'persona':
            return ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"], "1:1"
        elif nivel_a == 'persona':
            return ["CONGLOME", "VIVIENDA", "HOGAR"], "m:1"
        else:
            return ["CONGLOME", "VIVIENDA", "HOGAR"], "1:m"
    else:
        return ["CONGLOME", "VIVIENDA", "HOGAR"], "1:1"
```

---

## Variables — Convencion MAYUSCULAS

**Convencion OPEN DATA PERU:** Todas las variables ENAHO se trabajan en MAYUSCULAS (formato nativo INEI).

Al inicio de TODO script generado, incluir normalizacion:

**Python:**
```python
df.columns = df.columns.str.upper()  # Estandar OPEN DATA PERU
assert 'CONGLOME' in df.columns, "Variable CONGLOME no encontrada"
```

**R:**
```r
names(df) <- toupper(names(df))  # Estandar OPEN DATA PERU
stopifnot("CONGLOME" %in% names(df))
```

**Stata:**
```stata
rename *, upper  // Estandar OPEN DATA PERU
confirm variable CONGLOME
```

---

## Templates de Codigo

### Python (enahopy + pandas)

```python
# ============================================================
# OPEN DATA PERU — [TITULO]
# ============================================================

# --- BLOQUE 1: Librerias ---
import pandas as pd
import numpy as np
# pip install enahopy
from enahopy import consulta  # Descarga y carga de modulos ENAHO

# --- BLOQUE 2: Descarga ---
# enahopy descarga y descomprime automaticamente
# consulta(modulo, anio) retorna DataFrame
df_500 = consulta(500, 2024)

# --- BLOQUE 3: Normalizacion ---
df_500.columns = df_500.columns.str.upper()

# --- BLOQUE 4: Merge (si aplica) ---
# Merge persona-persona: llaves completas
df = pd.merge(df_200, df_500,
              on=["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"],
              how="inner",  # inner para conservar solo matches
              validate="1:1",  # Validar relacion esperada
              indicator=True)

# Verificar merge
print(df["_merge"].value_counts())
df = df.drop(columns=["_merge"])

# --- BLOQUE 5: Factor de expansion ---
# FACTOR07 para analisis general, FAC500A para modulo 500
# Sin factor = resultados NO representativos
media_ponderada = np.average(df["VARIABLE"], weights=df["FACTOR07"])
```

### R (enaho + srvyr)

```r
# ============================================================
# OPEN DATA PERU — [TITULO]
# ============================================================

# --- BLOQUE 1: Librerias ---
library(enaho)   # CRAN: descarga y carga ENAHO
library(haven)   # Lectura de .dta/.sav
library(dplyr)
library(srvyr)   # Survey-weighted analysis

# --- BLOQUE 2: Descarga y carga ---
# enaho::descargar.inei() descarga modulos del portal INEI
# enaho::leer.inei() carga archivos descargados
df_500 <- descargar.inei(2024, 5)  # anio, modulo

# --- BLOQUE 3: Normalizacion ---
names(df_500) <- toupper(names(df_500))

# --- BLOQUE 4: Merge ---
# Merge persona-persona
df <- inner_join(df_200, df_500,
                 by = c("CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"))

# Verificar duplicados post-merge
stopifnot(!any(duplicated(df[, c("CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO")])))

# --- BLOQUE 5: Diseno muestral con srvyr ---
# OBLIGATORIO para inferencia
df_svy <- df %>%
  as_survey_design(weights = FACTOR07)

# Estadisticos ponderados
df_svy %>%
  group_by(VARIABLE_GRUPO) %>%
  summarise(
    media = survey_mean(VARIABLE, vartype = "ci"),
    total = survey_total(VARIABLE, vartype = "ci")
  )
```

### Stata

```stata
* ============================================================
* OPEN DATA PERU — [TITULO]
* ============================================================

* --- BLOQUE 1: Instalacion ---
* ssc install enahodata  // Solo la primera vez

* --- BLOQUE 2: Descarga ---
enahodata download, year(2024) module(500)

* --- BLOQUE 3: Carga ---
use "ruta/enaho01a-2024-500.dta", clear
rename *, upper  // Estandar OPEN DATA PERU

* --- BLOQUE 4: Merge ---
* Merge persona-persona
merge 1:1 CONGLOME VIVIENDA HOGAR CODPERSO using "ruta/enaho01a-2024-300.dta"
tab _merge
keep if _merge == 3
drop _merge

* --- BLOQUE 5: Factor de expansion ---
* svyset para diseno muestral
svyset [pw=FACTOR07]
svy: mean VARIABLE
svy: tab VARIABLE_GRUPO
```

---

## Factores de Expansion — Referencia Rapida

| Factor | Nivel | Uso principal |
|---|---|---|
| FACTOR07 | persona | Analisis general: educacion (M300), salud (M400), gobernabilidad |
| FAC500A | persona | Especifico modulo 500 (empleo e ingreso) |
| FACTORANN | persona | Factor anual post-2012 (alternativa a FACTOR07) |
| FACTOR07_H | hogar | Analisis a nivel hogar: vivienda (M100), gastos, sumarias |
| FACPOB07 | hogar | Especifico para medicion de pobreza |

**REGLA:** Si el analisis es inferencial (medias, totales, proporciones poblacionales), el factor es OBLIGATORIO. Si es solo exploracion de datos (frecuencias muestrales, distribuciones), advertir que los resultados son muestrales.

---

## Representatividad

ENAHO tiene representatividad en estos niveles:
- **Nacional:** SI
- **Dominio geografico:** SI (8 dominios: Costa Norte/Centro/Sur, Sierra Norte/Centro/Sur, Selva, Lima Metropolitana)
- **Departamental:** SI (25 departamentos + Callao)
- **Provincial/Distrital:** NO — muestra insuficiente

Si el usuario necesita analisis provincial/distrital → sugerir **datos pooled** (ver `metodologia/append_pooled.md`).

---

## Restricciones

### NUNCA:
- Generar codigo con variables sin verificar en SQLite
- Producir estadisticos inferenciales sin factor de expansion
- Afirmar representatividad provincial/distrital con datos de un solo anio
- Mezclar niveles de analisis incompatibles (persona con hogar sin merge explicito)
- Presentar resultados exploratorios como conclusiones poblacionales
- Saltar la validacion del usuario antes de generar codigo

### SIEMPRE:
- Consultar SQLite antes de referenciar cualquier variable
- Esperar validacion del usuario despues de proponer modulos/variables
- Incluir comentarios didacticos en cada bloque de codigo
- Incluir validacion post-merge (N, duplicados, factor, missings)
- Advertir si una variable tiene alta tasa de missings
- Normalizar variables a MAYUSCULAS al inicio del script
- Generar el encabezado estandar ODP con modulos, anio, unidad, factor

---

## Catalogo de Modulos

Consultar `modulos/catalogo.md` para la tabla completa de 49 modulos con codigos, niveles y archivos.

Para busqueda rapida, consultar SQLite:
```python
conn.execute("SELECT codigo, nombre, nivel FROM modulos WHERE nombre LIKE ?", ("%empleo%",)).fetchall()
```

---

## Archivos de Referencia Metodologica

Cuando el flujo lo requiera, leer estos archivos para informacion detallada:
- `metodologia/unidades_analisis.md` — Reglas de unidad persona/hogar por modulo
- `metodologia/factores_expansion.md` — Que factor usar y por que
- `metodologia/deflactores.md` — IPCs y deflactacion de ingresos/gastos
- `metodologia/append_pooled.md` — Datos pooled para ganar muestra provincial/distrital

---

## Librerias de Referencia

| Libreria | Lenguaje | Repo | Funcion |
|---|---|---|---|
| enahopy | Python | github.com/elpapx/enahopy | Descarga y carga ENAHO |
| enaho | R | CRAN oficial | Descarga, carga, panel, ENDES |
| enahodata | Stata | github.com/MaykolMedrano/enahodata | Descarga y descompresion |
| PeruData | R | github.com/TJhon/PeruData | Referencia estructural |

---

*OPEN DATA PERU — Donny Tapara — Open Source — 2025*
