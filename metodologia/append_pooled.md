# Datos Pooled (Append Multi-Anio) — ENAHO

## El Problema

ENAHO tiene representatividad a nivel **nacional, dominio y departamental**, pero NO a nivel **provincial ni distrital**. El tamanio muestral por provincia/distrito es demasiado pequenio para inferencia confiable.

## La Solucion: Datos Pooled

Concatenar (append) datos de **multiples anios** del mismo modulo para ganar muestra. Esto permite:
- Obtener muestras suficientes a nivel provincial/distrital
- Mayor precision en dominios pequenios
- Analisis de tendencias con mas potencia estadistica

## Metodologia

### Paso 1: Seleccion de anios
- Usar anios consecutivos y cercanos (ej. 2020-2024)
- Evitar mezclar anios con cambios metodologicos grandes
- Verificar que las variables de interes existan en TODOS los anios (consultar SQLite)

### Paso 2: Carga y estandarizacion
- Cargar el mismo modulo para cada anio
- Agregar variable ANIO para identificar el periodo
- Verificar que las variables tengan la misma definicion entre anios

### Paso 3: Append (concatenacion vertical)
- Concatenar las bases de datos
- NO es un merge (horizontal) sino un append (vertical)

### Paso 4: Ajuste del factor de expansion
**CRITICO:** Al poolear K anios, el factor de expansion se divide entre K:

```
FACTOR_POOLED = FACTOR_ORIGINAL / K
```

Donde K = numero de anios pooleados. Esto evita sobreestimar la poblacion.

### Paso 5: Analisis con advertencia
- Los resultados pooled representan un **promedio del periodo**, no un anio especifico
- Documentar siempre: "Datos pooled ENAHO [anio_inicio]-[anio_fin], N=[total]"

## Implementacion

### Python
```python
import pandas as pd
import numpy as np

# --- Carga multi-anio ---
anios = [2020, 2021, 2022, 2023, 2024]
frames = []
for anio in anios:
    df_anio = cargar_modulo(500, anio)  # funcion de carga
    df_anio.columns = df_anio.columns.str.upper()
    df_anio["ANIO"] = anio
    frames.append(df_anio)

# --- Append ---
df_pooled = pd.concat(frames, ignore_index=True)

# --- Ajuste del factor ---
K = len(anios)
df_pooled["FACTOR_POOLED"] = df_pooled["FAC500A"] / K

# --- Verificar variables comunes ---
# Solo usar variables que existan en TODOS los anios
# Consultar SQLite para cada anio

# --- Analisis a nivel provincial ---
# Ahora con ~500,000 obs se puede desagregar mas
resultado = df_pooled.groupby("UBIGEO_PROV").apply(
    lambda x: np.average(x["VARIABLE"], weights=x["FACTOR_POOLED"])
)

print(f"Datos pooled {anios[0]}-{anios[-1]}, N={len(df_pooled):,}")
print("ADVERTENCIA: Resultados representan promedio del periodo")
```

### R
```r
library(dplyr)
library(srvyr)

# --- Carga multi-anio ---
anios <- 2020:2024
df_list <- lapply(anios, function(a) {
  df <- cargar_modulo(500, a)
  names(df) <- toupper(names(df))
  df$ANIO <- a
  df
})

# --- Append ---
df_pooled <- bind_rows(df_list)

# --- Ajuste del factor ---
K <- length(anios)
df_pooled <- df_pooled %>%
  mutate(FACTOR_POOLED = FAC500A / K)

# --- Diseno muestral pooled ---
df_svy <- df_pooled %>%
  as_survey_design(weights = FACTOR_POOLED)

# --- Analisis provincial ---
resultado <- df_svy %>%
  group_by(UBIGEO_PROV) %>%
  summarise(
    media = survey_mean(VARIABLE, vartype = "ci"),
    n = unweighted(n())
  )
```

### Stata
```stata
* --- Carga multi-anio ---
clear
tempfile pooled
save `pooled', replace emptyok

forval a = 2020/2024 {
    use "ruta/enaho01a-`a'-500.dta", clear
    rename *, upper
    gen ANIO = `a'
    append using `pooled'
    save `pooled', replace
}
use `pooled', clear

* --- Ajuste del factor ---
local K = 5
gen FACTOR_POOLED = FAC500A / `K'

* --- Diseno muestral ---
svyset [pw=FACTOR_POOLED]

* --- Analisis provincial ---
svy: mean VARIABLE, over(UBIGEO_PROV)
```

## Tamano de Muestra Minimo

Para que el analisis a nivel sub-departamental sea confiable:

| Nivel | N minimo recomendado | Anios pooled tipicos |
|---|---|---|
| Departamental | ~1,500 | 1 anio basta |
| Provincial | ~400 | 3-5 anios |
| Distrital | ~100-200 | 5-10 anios |

**ADVERTENCIA:** Incluso con pooled, algunos distritos rurales pequenios pueden tener N insuficiente. Siempre reportar el N por unidad geografica y excluir aquellos con N < 30.

## Verificacion de Consistencia Inter-Anual

Antes de poolear, verificar que no haya cambios metodologicos que invaliden la comparacion:

```python
# Consultar SQLite: variable existe en todos los anios?
for anio in anios:
    result = conn.execute("""
        SELECT COUNT(*) FROM variables v
        JOIN modulos m ON v.modulo_id = m.id
        WHERE m.codigo = ? AND v.anio = ? AND v.nombre = ?
    """, ("500", anio, "P507")).fetchone()
    if result[0] == 0:
        print(f"ADVERTENCIA: Variable P507 no encontrada en {anio}")
```

## Limitaciones

1. **No es un panel:** Los datos pooled tratan cada anio como muestra independiente. No se puede hacer seguimiento de individuos (excepto con panel ENAHO).
2. **Supuesto de estabilidad:** Se asume que la poblacion no cambio dramaticamente entre anios.
3. **Cambios en cuestionario:** Algunas variables cambian de nombre o definicion entre anios. Verificar en SQLite.
4. **Deflactar si hay variables monetarias:** Al poolear anios con diferente nivel de precios, deflactar primero (ver `deflactores.md`).
