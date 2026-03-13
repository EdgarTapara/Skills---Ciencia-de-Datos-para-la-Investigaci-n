# Unidades de Analisis — ENAHO

## Regla General

Cada modulo ENAHO tiene una **unidad de analisis** que determina que representa cada fila del dataset:

| Unidad | Llaves identificadoras | Descripcion |
|---|---|---|
| **Persona** | CONGLOME + VIVIENDA + HOGAR + CODPERSO | Una fila = una persona dentro de un hogar |
| **Hogar** | CONGLOME + VIVIENDA + HOGAR | Una fila = un hogar |

## Modulos por Unidad

### Nivel Persona
Cada fila es un individuo. Llaves: CONGLOME + VIVIENDA + HOGAR + CODPERSO

| Codigo | Modulo | Factor recomendado |
|---|---|---|
| 200 | Caracteristicas de los Miembros del Hogar | FACTOR07 |
| 300 | Educacion | FACTOR07 |
| 300A | Educacion (modulo adicional) | FACTOR07 |
| 400 | Salud | FACTOR07 |
| 500 | Empleo e Ingreso | FAC500A |
| 800A | Participacion Ciudadana (802-805) | FACTOR07 |
| 800B | Participacion Ciudadana (801, 806A) | FACTOR07 |
| GOB1 | Gobernabilidad (18+ anios) | FACTOR07 |

### Nivel Hogar
Cada fila es un hogar. Llaves: CONGLOME + VIVIENDA + HOGAR

| Codigo | Modulo | Nota |
|---|---|---|
| 100 | Caracteristicas de la Vivienda y del Hogar | Base de merge hogar |
| SUM8G | Sumaria por 8 Grupos de Gastos | Agregados monetarios |
| SUM12G | Sumaria por 12 Grupos de Gastos | Agregados monetarios |
| 700 | Programas Sociales Alimentarios | |
| 700A | Programas Sociales No Alimentarios | |
| 700B | Programas Sociales (711-713) | |
| GOB2 | Percepcion del Hogar (Jefe/Conyuge) | |
| ENH04-1 a ENH04-5 | Negocio (5 sub-modulos) | |
| 2000-2700 | Actividad Agropecuaria (8 sub-modulos) | Posible multi-fila por parcela |

### Nivel Hogar con Multiples Filas (CUIDADO)
Estos modulos estan marcados como `hogar` pero pueden tener multiples filas por hogar (una por item/producto):

| Codigo | Modulo | Razon multi-fila |
|---|---|---|
| 601 | Gastos en Alimentos y Bebidas | Una fila por producto alimentario |
| 602, 602A, 602B | Alimentos Inst. Beneficas | Una fila por programa/producto |
| 603 | Mantenimiento de la Vivienda | Una fila por tipo de gasto |
| 604 | Transportes y Comunicaciones | Una fila por tipo de gasto |
| 605 | Servicios a la Vivienda | Una fila por servicio |
| 606, 606D | Esparcimiento y Cuidados | Una fila por item |
| 607 | Vestido y Calzado | Una fila por item |
| 609 | Gastos de Transferencias | Una fila por transferencia |
| 610 | Muebles y Enseres | Una fila por item |
| 611 | Otros Bienes y Servicios | Una fila por item |
| 612 | Equipamiento del Hogar | Una fila por equipo |
| 613, 613H | Olla Comun | Una fila por item |
| 2100-2700 | Produccion Agropecuaria detalle | Una fila por cultivo/animal |

**REGLA:** Al hacer merge de un modulo hogar (1 fila por hogar) con un modulo de gastos (multiples filas), el resultado sera 1:m. Siempre verificar y documentar esto en el codigo.

## Como Determinar la Unidad

Antes de generar codigo, SIEMPRE:

1. Consultar el `nivel` del modulo en SQLite:
```python
conn.execute("SELECT nivel FROM modulos WHERE codigo = ?", (codigo,)).fetchone()
```

2. Preguntar al usuario: "Tu analisis es a nivel persona o a nivel hogar?"

3. Si el usuario quiere combinar persona + hogar:
   - Base: modulo persona (tiene mas filas)
   - Merge m:1 hacia modulo hogar (usando solo CONGLOME+VIVIENDA+HOGAR)
   - Factor: usar el del modulo persona (ej. FACTOR07 o FAC500A)

## Merge Mixto: Persona + Hogar

Ejemplo clasico: M500 (Empleo, persona) + Sumaria (hogar)

```python
# Base: M500 tiene ~100,000 filas (personas)
# Sumaria tiene ~35,000 filas (hogares)
df = pd.merge(
    df_500,                    # Izquierda: persona (muchas filas)
    df_sumaria,                # Derecha: hogar (pocas filas)
    on=["CONGLOME", "VIVIENDA", "HOGAR"],  # SIN CODPERSO
    how="left",                # Conservar todas las personas
    validate="m:1"             # Muchas personas por hogar
)
# Factor a usar: FAC500A (del modulo persona)
```
