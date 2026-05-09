# Charter Baseline v0.1 — mi-memoria

## Documento Fundacional

| Campo | Valor |
|---|---|
| Proyecto Runtime | `mi-memoria` |
| Tipo | Skill Runtime Local |
| Baseline Version | `v0.1` |
| Baseline Mode | `A — Core CLI Skill` |
| Stack Inicial | `Python` |
| Estado | Draft aprobado para implementación |
| Arquitectura | Minimalista, incremental y extensible |
| Fecha | 2026-05-08 |

---

# 1. Propósito

`mi-memoria` es un runtime local de skills diseñado para operar sobre repositorios de conocimiento Markdown.

El runtime NO es el vault de conocimiento.

El runtime es un proyecto independiente cuya responsabilidad es:

- capturar;
- normalizar;
- clasificar;
- validar;
- consolidar;
- registrar memoria curada;
- operar sobre un repositorio de conocimiento externo.

La versión `v0.1` define exclusivamente la baseline operacional mínima para el primer skill funcional.

---

# 2. Separación Arquitectónica Obligatoria

## 2.1 Runtime Repository

Repositorio técnico que contiene:

- skills;
- CLI;
- scripts;
- harnesses;
- memoria operacional;
- lógica de ejecución.

Ejemplo:

```text
mi-memoria/
```

---

## 2.2 Vault Repository

Repositorio de conocimiento Markdown.

Debe contener únicamente:

- notas;
- assets;
- taxonomía;
- referencias;
- memoria consolidada.

Ejemplo:

```text
mi-memoria-vault/
```

---

## 2.3 Regla No Negociable

El vault NO debe contener:

- runtimes;
- dependencias Python;
- scripts operacionales;
- logs;
- temporales;
- automatización interna;
- lógica agentic.

El runtime opera SOBRE el vault.

Nunca DENTRO del vault.

---

# 3. Filosofía Arquitectónica

## 3.1 Minimalismo operacional

Toda complejidad debe justificarse mediante:

- necesidad operacional real;
- repetibilidad verificable;
- reducción concreta de trabajo manual;
- mejora observable de consistencia.

---

## 3.2 Evolución progresiva

La solución debe crecer incrementalmente:

```text
v0.1 → v0.2 → v0.3 → v1.x
```

Sin introducir:

- infraestructura innecesaria;
- agentes autónomos;
- dependencias externas prematuras;
- sistemas distribuidos;
- complejidad aspiracional.

---

## 3.3 Skills pequeños y desacoplados

Cada skill debe:

- resolver una responsabilidad concreta;
- poseer activación clara;
- operar con contexto limitado;
- producir salidas verificables;
- poder evolucionar independientemente.

---

## 3.4 Memoria reflexiva y curada

La memoria persistente NO debe ser una copia indiscriminada de conversaciones.

La memoria debe conservar exclusivamente:

- decisiones;
- convenciones;
- taxonomías;
- aprendizajes persistentes;
- cambios relevantes;
- acuerdos operacionales;
- restricciones aprobadas.

La memoria debe ser:

- verificable;
- resumida;
- reflexiva;
- trazable;
- útil operacionalmente.

---

# 4. Primer Skill Oficial

## Nombre

```text
normalize
```

---

## Responsabilidad

Transformar entradas Markdown libres en notas consistentes para un vault Obsidian.

Debe producir:

- estructura estándar;
- frontmatter consistente;
- taxonomía básica;
- nombres de archivo estables;
- wikilinks sugeridos;
- validaciones verificables;
- salidas reproducibles.

---

# 5. Modelo de Activación

## 5.1 Slash Command

Activación principal:

```text
/mi-memoria
```

Ejemplos:

```text
/mi-memoria normalize
/mi-memoria remember
/mi-memoria validate
```

---

## 5.2 Activación natural

Ejemplos válidos:

```text
Organiza esta nota.
Convierte esta idea en una nota estructurada.
Clasifica este Markdown.
Normaliza esta nota.
Guarda esta decisión como memoria.
```

---

## 5.3 Activación máquina/script

```bash
mi-memoria run normalize --input note.md
mi-memoria validate --input note.md
mi-memoria remember --summary "..."
```

---

# 6. Workspace Operacional

## 6.1 Objetivo

El runtime debe operar inicialmente sobre un workspace transitorio.

Esto evita:

- búsquedas complejas;
- modificaciones accidentales del vault;
- automatización riesgosa;
- operaciones masivas prematuras.

---

## 6.2 Estructura mínima

```text
workspace/
  inbox/
  processing/
  preview/
  exports/
```

---

## 6.3 Flujo operacional

### Captura

Las notas ingresan inicialmente a:

```text
workspace/inbox/
```

---

### Procesamiento

El skill:

- normaliza;
- clasifica;
- valida;
- genera preview;
- propone ubicación final.

---

### Consolidación

La escritura al vault requiere operación explícita.

Ejemplo:

```bash
/mi-memoria apply
```

---

## 6.4 Integridad obligatoria

Todo movimiento debe:

- ser atómico;
- registrar timestamp;
- registrar origen;
- registrar destino;
- registrar resultado;
- evitar sobrescrituras silenciosas.

---

# 7. Método de Memoria Persistente

## Nombre inicial

```text
remember
```

---

## Objetivo

Persistir memoria curada y reflexiva.

NO almacenar conversaciones completas.

---

## Contenido permitido

- decisiones arquitectónicas;
- convenciones aprobadas;
- cambios relevantes;
- acuerdos operacionales;
- taxonomías;
- restricciones;
- aprendizajes persistentes.

---

## Contenido prohibido

- razonamientos temporales;
- cadenas completas de chat;
- ruido iterativo;
- snapshots indiscriminados;
- memoria redundante.

---

## Estructura propuesta

```text
memory/
  hot/
  history/
  conventions/
```

---

# 8. Skill Setup Inicial

## Script obligatorio

```text
scripts/skill_setup.sh
```

---

## Responsabilidad

El script debe permitir inicializar un vault compatible desde la raíz de otro repositorio.

El runtime NO crea su propio vault interno.

---

## Comportamiento esperado

Ejemplo:

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
```

Debe:

- crear estructura base;
- crear taxonomía inicial;
- crear carpetas mínimas;
- crear archivos `.gitkeep` cuando aplique;
- crear templates mínimos;
- validar permisos;
- evitar sobrescribir estructuras existentes.

---

## Estructura mínima del vault

```text
mi-memoria-vault/

├── 00-inbox/
├── 10-areas/
├── 20-projects/
├── 30-resources/
├── 40-archive/

├── assets/
├── templates/
├── indexes/

└── memory/
```

---

# 9. Estructura del Runtime

```text
mi-memoria/

├── README.md
├── AGENTS.md
├── SKILL.md
├── CHANGELOG.md
├── Makefile
├── .gitignore
├── .env.example

├── docs/
│   ├── architecture.md
│   ├── activation.md
│   ├── usage.md
│   ├── validation.md
│   └── scope-governance.md

├── skills/
│   └── normalize/
│       ├── SKILL.md
│       ├── examples/
│       ├── templates/
│       └── references/

├── workspace/
│   ├── inbox/
│   ├── processing/
│   ├── preview/
│   └── exports/

├── cli/
├── bin/
├── scripts/

├── memory/
│   ├── hot/
│   ├── history/
│   └── conventions/

├── harnesses/
│   ├── restrictions.md
│   ├── behavior-limits.md
│   └── acceptance-checks.md

├── logs/
│   └── .gitkeep

├── tmp/
│   └── .gitkeep

└── .github/
    └── copilot-instructions.md
```

---

# 10. Capacidades P0 Obligatorias

## 10.1 Ingesta de contenido

Debe aceptar:

- texto plano;
- Markdown;
- input CLI;
- archivos `.md`.

---

## 10.2 Normalización Markdown

Debe producir:

```md
---
title:
type:
status:
created:
updated:
tags:
aliases:
source:
---

# Título

## Resumen

## Desarrollo

## Relaciones

## Pendientes
```

---

## 10.3 Frontmatter Obsidian

Campos mínimos:

| Campo | Requerido |
|---|---|
| title | Sí |
| type | Sí |
| status | Sí |
| created | Sí |
| updated | Sí |
| tags | Sí |

---

## 10.4 Clasificación básica

Taxonomía inicial:

```text
00-inbox/
10-areas/
20-projects/
30-resources/
40-archive/
```

---

## 10.5 Naming consistente

Formato:

```text
yyyy-mm-dd-slug.md
```

---

## 10.6 Wikilinks sugeridos

Debe proponer:

```md
[[concepto]]
[[nota-relacionada]]
```

Usando heurísticas simples locales.

---

## 10.7 Validación

Debe validar:

- estructura;
- frontmatter;
- tags;
- nombres;
- tipos;
- estados;
- Markdown mínimo esperado.

---

## 10.8 Preview seguro

Debe existir:

```bash
--preview
```

Antes de cualquier escritura.

---

## 10.9 Escritura controlada

Debe requerir:

```bash
--write
```

Para modificar archivos.

---

# 11. CLI Obligatoria

## Human CLI

Ejemplos:

```bash
mi-memoria ask "organiza esta nota"
mi-memoria ask "normaliza este markdown"
mi-memoria explain
mi-memoria context
```

---

## Machine CLI

Ejemplos:

```bash
mi-memoria run normalize --input note.md --json
mi-memoria validate --input note.md
mi-memoria capabilities --json
```

---

# 12. Seguridad

## Reglas obligatorias

El skill NO debe:

- ejecutar comandos arbitrarios;
- modificar fuera del vault permitido;
- sobrescribir automáticamente;
- borrar archivos;
- revelar secretos;
- escribir silenciosamente;
- operar sin preview cuando exista ambigüedad.

---

## Escritura segura

Toda escritura debe:

- requerir confirmación o flag explícito;
- generar log local;
- poder rastrearse;
- evitar destrucción accidental.

---

# 13. Variables de Entorno

## Política v0.1

La versión inicial debe minimizar dependencias de entorno.

Permitido:

```text
MI_MEMORIA_VAULT_PATH=
```

Opcional:

```text
MI_MEMORIA_DEFAULT_LANGUAGE=es
```

---

## No requerido en v0.1

- secretos;
- API keys;
- OAuth;
- tokens;
- servicios externos.

---

# 14. Gitignore Obligatorio

```gitignore
logs/*
tmp/*

.env
.env.local

__pycache__/
.pytest_cache/
dist/
build/

!logs/.gitkeep
!tmp/.gitkeep
!.env.example
```

---

# 15. MCP Strategy

## Decisión explícita

```text
Referenciado para evolución futura.
NO implementado en v0.1.
```

---

# 16. HTTPS Strategy

## Decisión explícita

```text
No aplica en v0.1.
```

Toda operación será local vía CLI.

---

# 17. Harnesses

## Objetivo

Evitar deriva del skill.

---

## Restricciones mínimas

El skill debe:

- producir Markdown válido;
- mantener frontmatter consistente;
- evitar inventar metadata innecesaria;
- evitar complejidad excesiva;
- priorizar claridad sobre creatividad.

---

# 18. Criterios de Aceptación

La v0.1 se considera válida cuando:

- el CLI funciona localmente;
- el skill normaliza Markdown consistentemente;
- existen previews verificables;
- existen validaciones mínimas;
- existe memoria curada persistente;
- existe workspace operacional;
- existe setup del vault;
- el runtime es autoexplicable;
- no existen dependencias externas obligatorias;
- la estructura del repo es coherente;
- los cambios son trazables.

---

# 19. Decisiones Arquitectónicas Aceptadas

| Decisión | Estado |
|---|---|
| Python local | Aprobado |
| Baseline A | Aprobado |
| Runtime separado del vault | Aprobado |
| Workspace transitorio | Aprobado |
| Memoria reflexiva | Aprobado |
| Slash activation | Aprobado |
| Obsidian como formato, no runtime | Aprobado |
| Sin APIs externas | Aprobado |
| Sin HTTPS | Aprobado |
| Sin MCP funcional | Aprobado |
| Skills pequeños | Aprobado |
| Evolución incremental | Aprobado |

---

# 20. Riesgos Reconocidos

| Riesgo | Mitigación |
|---|---|
| Crecimiento descontrolado del scope | Scope governance |
| Skill spaghetti | Skills desacoplados |
| Sobrediseño agentic | Minimalismo |
| Automatización destructiva | Preview obligatorio |
| Taxonomía excesiva | Clasificación mínima |
| Dependencias futuras innecesarias | Baseline incremental |
| Memoria basura | Curación reflexiva |

---

# 21. Próximos Pasos

## P0

Implementar:

- CLI mínima;
- normalize;
- workspace;
- preview;
- apply;
- remember;
- validación;
- setup del vault;
- harnesses;
- memoria inicial.

---

## P1 futuro

Posibles evoluciones:

- indexado local;
- búsqueda contextual;
- referencias cruzadas avanzadas;
- servicios externos desacoplados;
- interoperabilidad;
- MCP bridge;
- runtime HTTPS.

---

# 22. Iteration History

## v0.1 — 2026-05-08

### Decisiones

- Se adopta Baseline A.
- Se separa runtime del vault.
- Se adopta Python local.
- Se adopta arquitectura incremental.
- Se incorpora workspace operacional.
- Se incorpora memoria reflexiva curada.
- Se adopta slash activation.
- Se define setup externo del vault.

### Diferidos

- MCP
- HTTPS
- APIs externas
- Multi-agent
- RAG/vector DB

### Motivación

Construir una base estable, verificable y sostenible antes de introducir complejidad adicional.
