# Deflactores — ENAHO

## Cuando Deflactar

Deflactar es necesario cuando:
- Se comparan ingresos o gastos entre **diferentes anios** (analisis multi-anio/pooled)
- Se quiere expresar valores monetarios en **soles constantes** de un anio base

NO es necesario cuando:
- Se trabaja con un solo anio
- Las variables no son monetarias
- Se usan las variables de Sumaria que ya vienen deflactadas por INEI

## Variables de Ingreso que Requieren Deflactar

Del modulo 500 (Empleo e Ingreso):
- I524A1: Ingreso por trabajo principal
- D529T: Ingreso total por trabajo
- I530A: Ingreso por trabajo secundario
- I538A1: Ingreso por trabajo independiente

De Sumaria:
- INGHOG1D a INGHOG2D: Ingresos del hogar (YA deflactados por INEI)
- GASHOG1D a GASHOG2D: Gastos del hogar (YA deflactados por INEI)

**REGLA:** Las variables de Sumaria con sufijo "D" ya estan deflactadas. NO deflactar dos veces.

## Indice de Precios al Consumidor (IPC)

Para deflactar manualmente, se usa el IPC base 2009=100 publicado por INEI/BCRP.

### Valores IPC referenciales (Lima Metropolitana, promedio anual)

| Anio | IPC (base 2009=100) |
|---|---|
| 2015 | 114.81 |
| 2016 | 118.87 |
| 2017 | 122.63 |
| 2018 | 124.28 |
| 2019 | 126.93 |
| 2020 | 129.32 |
| 2021 | 134.57 |
| 2022 | 145.32 |
| 2023 | 150.10 |
| 2024 | 153.50 (estimado) |

**NOTA:** Verificar valores actualizados en:
- BCRP: https://estadisticas.bcrp.gob.pe
- INEI: Series de IPC mensual

### Deflactores espaciales (por dominio)

INEI publica deflactores espaciales por dominio geografico que ajustan por diferencias de precios entre regiones. Estos se encuentran en la documentacion metodologica de la Sumaria de cada anio.

## Implementacion

### Formula
```
valor_real = valor_nominal * (IPC_base / IPC_periodo)
```

### Python
```python
# Deflactar ingresos a soles constantes de 2020
IPC_BASE = 129.32  # 2020
IPC_ACTUAL = 153.50  # 2024

df["INGRESO_REAL"] = df["I524A1"] * (IPC_BASE / IPC_ACTUAL)

# Comentario didactico:
# Deflactamos el ingreso nominal a soles de 2020
# para comparabilidad inter-temporal
```

### R
```r
# Deflactar
IPC_BASE <- 129.32  # 2020
IPC_ACTUAL <- 153.50  # 2024

df <- df %>%
  mutate(INGRESO_REAL = I524A1 * (IPC_BASE / IPC_ACTUAL))
```

### Stata
```stata
* Deflactar
local ipc_base = 129.32
local ipc_actual = 153.50

gen INGRESO_REAL = I524A1 * (`ipc_base' / `ipc_actual')
label variable INGRESO_REAL "Ingreso real (soles 2020)"
```

## Advertencias

1. **Sumaria "D":** Variables que terminan en "D" en Sumaria (ej. INGHOG1D) ya fueron deflactadas por INEI. No deflactar de nuevo.
2. **Deflactores espaciales:** Para comparaciones regionales rigurosas, usar los deflactores espaciales de INEI (publicados con cada Sumaria).
3. **Verificar fuente:** Siempre citar la fuente del IPC usado y el anio base.
