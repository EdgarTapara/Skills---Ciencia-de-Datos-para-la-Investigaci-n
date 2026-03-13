# Catalogo de Modulos ENAHO

> Fuente: SQLite enaho_variables.db | Anios disponibles: 2015, 2020, 2024

## Modulos Principales

### Nivel Persona (llaves: CONGLOME + VIVIENDA + HOGAR + CODPERSO)

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| 200 | Caracteristicas de los Miembros del Hogar | ENAHO01-YYYY-200.SAV | 39 |
| 300 | Educacion | ENAHO01A-YYYY-300.SAV | 478 |
| 300A | Educacion (modulo adicional) | ENAHO01A-YYYY-300A.SAV | - |
| 400 | Salud | ENAHO01A-YYYY-400.SAV | 902 |
| 500 | Empleo e Ingreso | ENAHO01A-YYYY-500.SAV | 1,228 |
| 800A | Participacion Ciudadana (802-805) | ENAHO01-YYYY-800A.SAV | 33 |
| 800B | Participacion Ciudadana (801, 806A) | ENAHO01-YYYY-800B.SAV | 15 |
| GOB1 | Gobernabilidad (18+ anios) | ENAHO01B-YYYY-1.SAV | 320 |

### Nivel Hogar — Base (llaves: CONGLOME + VIVIENDA + HOGAR)

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| 100 | Caracteristicas de la Vivienda y del Hogar | ENAHO01-YYYY-100.SAV | 329 |
| SUM8G | Sumaria por 8 Grupos de Gastos | Sumaria-YYYY-8g.SAV | 163 |
| SUM12G | Sumaria por 12 Grupos de Gastos | Sumaria-YYYY-12g.SAV | 240 |
| GOB2 | Percepcion del Hogar (Jefe/Conyuge) | ENAHO01B-YYYY-2.SAV | 94 |

### Nivel Hogar — Programas Sociales

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| 700 | Programas Sociales Alimentarios | ENAHO01-YYYY-700.SAV | 47 |
| 700A | Programas Sociales No Alimentarios | ENAHO01-YYYY-700A.SAV | 26 |
| 700B | Programas Sociales (711-713) | ENAHO01-YYYY-700B.SAV | 19 |

### Nivel Hogar — Gastos (posible multi-fila por hogar)

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| 601 | Gastos en Alimentos y Bebidas | ENAHO01-YYYY-601.SAV | 37 |
| 602 | Alimentos Inst. Beneficas (dentro hogar) | ENAHO01-YYYY-602.SAV | 23 |
| 602A | Alimentos Inst. Beneficas (fuera, <14) | ENAHO01-YYYY-602A.SAV | 24 |
| 602B | Alimentos Inst. Beneficas B (dentro hogar) | ENAHO01-YYYY-602B.SAV | 17 |
| 603 | Mantenimiento de la Vivienda | ENAHO01-YYYY-603.SAV | 47 |
| 604 | Transportes y Comunicaciones | ENAHO01-YYYY-604.SAV | 45 |
| 605 | Servicios a la Vivienda | ENAHO01-YYYY-605.SAV | 37 |
| 606 | Esparcimiento, Diversion y Cultura | ENAHO01-YYYY-606.SAV | 45 |
| 606D | Bienes y Servicios Cuidados Personales | ENAHO01-YYYY-606D.SAV | 46 |
| 607 | Vestido y Calzado | ENAHO01-YYYY-607.SAV | 46 |
| 609 | Gastos de Transferencias | ENAHO01-YYYY-609.SAV | 16 |
| 610 | Muebles y Enseres | ENAHO01-YYYY-610.SAV | 46 |
| 611 | Otros Bienes y Servicios | ENAHO01-YYYY-611.SAV | 43 |
| 612 | Equipamiento del Hogar | ENAHO01-YYYY-612.SAV | 23 |
| 613 | Olla Comun | ENAHO01-YYYY-613.SAV | 45 |
| 613H | Alimentos Olla Comun — Correspondencia | ENAHO01-YYYY-613H.SAV | 20 |

### Nivel Hogar — Negocio

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| ENH04-1 | Caracteristicas Basicas (Preg. 1-13) | ENAHO04-YYYY-1.SAV | 63 |
| ENH04-2 | Produccion de Bienes (Preg. 14-22) | ENAHO04-YYYY-2.SAV | 18 |
| ENH04-3 | Otros Gastos (Preg. 23) | ENAHO04-YYYY-3.SAV | 18 |
| ENH04-4 | Mano de Obra y Empleo (Preg. 24) | ENAHO04-YYYY-4.SAV | 24 |
| ENH04-5 | Hoja de Control (Preg. 25) | ENAHO04-YYYY-5.SAV | 19 |

### Nivel Hogar — Actividad Agropecuaria (posible multi-fila)

| Codigo | Nombre | Archivo Base | Variables (2024) |
|---|---|---|---|
| 2000 | Actividad Agropecuaria | ENAHO02-YYYY-2000.SAV | 24 |
| 2000A | Actividad Agropecuaria A | ENAHO02-YYYY-2000A.SAV | 28 |
| 2100 | Produccion Agricola | ENAHO02-YYYY-2100.SAV | 34 |
| 2200 | Subproductos Agricolas | ENAHO02-YYYY-2200.SAV | 29 |
| 2300 | Produccion Forestal | ENAHO02-YYYY-2300.SAV | 21 |
| 2400 | Gastos Agricolas y Forestales | ENAHO02-YYYY-2400.SAV | 28 |
| 2500 | Produccion Pecuaria | ENAHO02-YYYY-2500.SAV | 43 |
| 2600 | Subproductos Pecuarios | ENAHO02-YYYY-2600.SAV | 27 |
| 2700 | Gastos en Actividades Pecuarias | ENAHO02-YYYY-2700.SAV | 21 |

## Variables Clave Transversales

Estas variables aparecen en la mayoria de modulos y son fundamentales para merge e identificacion:

| Variable | Descripcion | Presente en |
|---|---|---|
| CONGLOME | Numero de Conglomerado | Todos |
| VIVIENDA | Numero de Vivienda | Todos |
| HOGAR | Numero de Hogar | Todos |
| CODPERSO | Codigo de Persona | Modulos persona |
| UBIGEO | Ubicacion Geografica (6 digitos) | Todos |
| DOMINIO | Dominio Geografico (8 dominios) | Todos |
| ESTRATO | Estrato Geografico | Todos |
| MES | Mes de Ejecucion | Todos |
| FACTOR07 | Factor de Expansion (met. 2007) | M200-M400, M800 |
| FAC500A | Factor de Expansion M500 | Solo M500 |
| FACTOR07_H | Factor de Expansion Hogar | M100, Sumarias |

## Consulta Rapida en SQLite

```python
import sqlite3
conn = sqlite3.connect("metadata/enaho_variables.db")

# Todos los modulos
conn.execute("SELECT codigo, nombre, nivel FROM modulos ORDER BY codigo").fetchall()

# Variables de un modulo en un anio
conn.execute("""
    SELECT v.nombre, v.etiqueta, v.tipo
    FROM variables v JOIN modulos m ON v.modulo_id = m.id
    WHERE m.codigo = '500' AND v.anio = 2024
    ORDER BY v.nombre
""").fetchall()

# Buscar variable por nombre
conn.execute("""
    SELECT v.nombre, v.etiqueta, m.codigo, v.anio
    FROM variables v JOIN modulos m ON v.modulo_id = m.id
    WHERE v.nombre LIKE '%P507%'
""").fetchall()
```
