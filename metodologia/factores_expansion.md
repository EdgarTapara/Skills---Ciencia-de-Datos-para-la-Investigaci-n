# Factores de Expansion — ENAHO

## Que son

Los factores de expansion permiten extrapolar los resultados de la muestra ENAHO a la poblacion total del Peru. Sin factor, los resultados son MUESTRALES, no poblacionales.

## Factores Disponibles

| Factor | Nivel | Descripcion | Cuando usar |
|---|---|---|---|
| **FACTOR07** | persona | Factor anualizado metodologia 2007 | Default para modulos persona (300, 400, GOB1, 800) |
| **FAC500A** | persona | Factor anualizado modulo 500 | Especifico para Empleo e Ingreso |
| **FACTORANN** | persona | Factor anual post-2012 | Alternativa a FACTOR07 |
| **FACTOR07_H** | hogar | Factor anualizado hogar (met. 2007) | Modulos hogar: 100, gastos, sumarias |
| **FACPOB07** | hogar | Factor de pobreza (met. 2007) | Especifico para medicion de pobreza |

## Reglas de Asignacion

### Por modulo

| Modulo | Factor | Razon |
|---|---|---|
| M200 (Miembros Hogar) | FACTOR07 | Persona - general |
| M300 (Educacion) | FACTOR07 | Persona - general |
| M400 (Salud) | FACTOR07 | Persona - general |
| M500 (Empleo) | **FAC500A** | Factor propio del modulo |
| M100 (Vivienda) | FACTOR07_H | Hogar |
| Sumarias | FACTOR07_H | Hogar |
| Gastos (601-613) | FACTOR07_H | Hogar |
| GOB1 (Gobernabilidad) | FACTOR07 | Persona |
| GOB2 (Percepcion) | FACTOR07_H | Hogar |
| Agropecuarios (2000+) | FACTOR07_H | Hogar |

### Merge mixto (persona + hogar)

Cuando se combinan modulos de diferente nivel, el factor depende de la UNIDAD DE ANALISIS FINAL:

- Si el analisis es POR PERSONA (ej. tasa de desempleo por nivel educativo): usar factor de **persona** (FACTOR07 o FAC500A)
- Si el analisis es POR HOGAR (ej. gasto promedio por hogar segun jefe): usar factor de **hogar** (FACTOR07_H)

## Implementacion

### Python
```python
import numpy as np

# Media ponderada
media = np.average(df["VARIABLE"], weights=df["FACTOR07"])

# Tabla ponderada
df["VARIABLE_POND"] = df["VARIABLE"] * df["FACTOR07"]
total = df["VARIABLE_POND"].sum() / df["FACTOR07"].sum()
```

### R (con srvyr — RECOMENDADO)
```r
library(srvyr)

# Diseño muestral
df_svy <- df %>% as_survey_design(weights = FACTOR07)

# Media ponderada con IC
df_svy %>% summarise(media = survey_mean(VARIABLE, vartype = "ci"))

# Proporcion ponderada
df_svy %>%
  group_by(GRUPO) %>%
  summarise(prop = survey_mean(vartype = "ci"))
```

### Stata
```stata
* Declarar diseño muestral
svyset [pw=FACTOR07]

* Media ponderada
svy: mean VARIABLE

* Proporcion
svy: proportion VARIABLE_CAT

* Tabulacion
svy: tab VARIABLE1 VARIABLE2
```

## Validacion del Factor

Incluir en todo script:
```python
# Verificar factor presente y valido
assert df["FACTOR07"].notna().all(), "Hay missings en el factor de expansion"
assert (df["FACTOR07"] > 0).all(), "Hay factores negativos o cero"
print(f"Factor - Min: {df['FACTOR07'].min():.0f}, Max: {df['FACTOR07'].max():.0f}, Media: {df['FACTOR07'].mean():.0f}")
```
