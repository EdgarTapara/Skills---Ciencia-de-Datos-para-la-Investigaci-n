# SKILL-ODP: Open Data Peru

Skill de IA para analisis metodologicamente correcto de la Encuesta Nacional de Hogares (ENAHO) del INEI - Peru.

## Que es

SKILL-ODP es una **skill para asistentes de IA** (Claude Code, Claude AI, Antigravity, etc.) que estandariza y profesionaliza la generacion de codigo para analisis de datos ENAHO. Genera codigo en **Python, R y Stata** siguiendo las mejores practicas metodologicas del INEI.

## Problema que resuelve

Los investigadores usan IA para generar codigo ENAHO, pero el codigo resultante:
- No verifica que las variables existan en el modulo/anio correcto
- No usa factores de expansion (resultados no representativos)
- Mezcla niveles de analisis (persona vs hogar) sin las llaves correctas
- No advierte sobre representatividad provincial/distrital

SKILL-ODP resuelve esto con reglas metodologicas estrictas y una base de datos de metadatos.

## Instalacion

### Claude Code
```bash
# Copiar la carpeta SKILL-ODP a ~/.claude/skills/
cp -r SKILL-ODP ~/.claude/skills/SKILL-ODP
```

### Otros asistentes
Cargar el archivo `SKILL.md` como contexto/instrucciones del asistente.

## Estructura

```
SKILL-ODP/
├── SKILL.md                     # Skill principal (el cerebro)
├── README.md                    # Este archivo
├── metadata/
│   └── enaho_variables.db       # SQLite con 12,700+ variables ENAHO
├── metodologia/
│   ├── unidades_analisis.md     # Reglas persona/hogar por modulo
│   ├── factores_expansion.md    # Que factor usar y cuando
│   ├── deflactores.md           # IPCs y deflactacion de ingresos
│   └── append_pooled.md         # Datos pooled para nivel provincial
├── modulos/
│   └── catalogo.md              # 49 modulos ENAHO documentados
└── tests/
    └── test_merges.py           # Tests de merge para todos los modulos
```

## Como usar

1. Instalar la skill en tu asistente de IA
2. Decir: **"usemos ODP"** o **"analicemos datos ENAHO"**
3. La skill guia una conversacion:
   - Pregunta tu objetivo de investigacion
   - Sugiere lenguaje (Python/R/Stata)
   - Propone modulos y variables (verificados en SQLite)
   - Genera codigo con factor de expansion, llaves correctas, validacion

## Base de Datos de Metadatos

La SQLite (`metadata/enaho_variables.db`) contiene:
- **49 modulos** ENAHO catalogados
- **12,700+ variables** para anios 2015, 2020 y 2024
- **Categorias** con etiquetas y valores centinela
- **Llaves de union** entre modulos
- **Factores de expansion** por anio y nivel

## Lenguajes Soportados

| Lenguaje | Libreria | Cobertura |
|---|---|---|
| Python | enahopy + pandas | Descarga, carga, merge, analisis |
| R | enaho + srvyr | Descarga, carga, diseno muestral |
| Stata | enahodata | Descarga, carga, analisis nativo |

## Roadmap

- **v0.1** (Mar 2025): Skill base — flujo conversacional, merge cualquier modulo, Python/R/Stata
- **v0.2**: Limpieza de centinelas, exploratoria, validacion avanzada
- **v0.3**: Deflactores, datos pooled, publicacion GitHub
- **v0.4**: ML e imputacion
- **v0.5**: MCP server, memoria de sesion
- **v1.0**: Agente autonomo open source
- **v2.0**: Expansion a ENDES, EPEN, CENSOS

## Autor

**Donny Tapara**
Estudiante de Economia | Talento COFIDE | Arequipa, Peru

## Licencia

MIT
