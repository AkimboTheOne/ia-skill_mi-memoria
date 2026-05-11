# mi-memoria

![version](https://img.shields.io/badge/version-v0.4.2-blue)
![maturity](https://img.shields.io/badge/maturity-p4--stable-brightgreen)
![tests](https://img.shields.io/badge/tests-make%20test%20passing-success)
![license](https://img.shields.io/badge/license-not%20declared-lightgrey)
![roadmap](https://img.shields.io/badge/roadmap-P5%20deferred-orange)

Runtime local de skills para operar sobre repositorios de conocimiento Markdown, separado del vault de conocimiento.

`mi-memoria` v0.4.2 implementa baseline + P1/P2/P3/P4 (hardening):

- CLI local sin dependencias externas obligatorias.
- Skill `normalize` para convertir texto o Markdown libre en notas Obsidian consistentes.
- Validación de estructura, frontmatter, nombres y secciones mínimas.
- Workspace técnico del runtime y workspace curatorial visible dentro del vault.
- Escritura controlada hacia un vault externo.
- Memoria curada del proyecto en el vault mediante `remember`.
- Generación determinista de plantillas mediante `template`.
- Setup inicial de vault mediante `scripts/skill_setup.sh`.
- Actualización segura del runtime mediante `upgrade`.

## Activación por agente y CLI

Formas de invocar el skill en flujos humanos y de agentes:

1. Slash command para agentes conversacionales:
- `/mi-memoria capture "Idea inicial"`
- `/mem review --path workspace/inbox`

2. Convención prompt-style usada en algunos coding CLIs:
- `$mi-memoria summarize --path workspace/inbox`
- `$mem context-build --topic "arquitectura local"`

3. Contrato técnico ejecutable (canónico):
- `./bin/mi-memoria <comando>`
- `./bin/mi-memoria capabilities --json`

4. Flujo mínimo recomendado por intención:
- Capturar: `./bin/mi-memoria capture --kind idea --text "..." --json`
- Validar/Clasificar: `./bin/mi-memoria classify --input workspace/inbox/<nota>.md --json`
- Revisar: `./bin/mi-memoria review --path workspace/inbox --json`
- Publicar: `./bin/mi-memoria publish --path workspace/inbox --format markdown --output workspace/exports/pack --json`

`$mi-memoria` y `$mem` son convenciones de invocación de agentes. El contrato técnico ejecutable y verificable del repositorio sigue siendo `./bin/mi-memoria`.

### Alcance del repositorio

- Runtime local de conocimiento Markdown (sin dependencias externas obligatorias).
- Separación estricta runtime/vault; el vault no contiene lógica operacional.
- Madurez actual: `p4-stable` con hardening previo a P5.
- P5 (MCP/HTTPS/proveedores externos) permanece diferida y no ejecutada.
- Operaciones críticas con control explícito (`preview`, `apply`, `--write` según comando).

## Instalación del skill

La forma recomendada para usar `mi-memoria` dentro de un repo compartido con Codex es instalarlo como submódulo Git en `.agents/skills/`:

```bash
git submodule add https://github.com/AkimboTheOne/ia-skill_mi-memoria.git .agents/skills/ia-skill_mi-memoria
git submodule update --init --recursive
```

Esto mantiene el skill como componente versionado e independiente del vault. En instalaciones nuevas, quienes clonen el repo principal pueden usar:

```bash
git clone --recurse-submodules <URL_DEL_REPO>
```

Si el repo ya fue clonado sin submódulos:

```bash
git submodule update --init --recursive
```

Ubicaciones comunes según agente:

| Agente | Instalación en repo | Instalación global |
|---|---|---|
| Codex | `.agents/skills/ia-skill_mi-memoria/` | `~/.agents/skills/` o `~/.codex/skills/` |
| Claude | `.claude/skills/ia-skill_mi-memoria/` | `~/.claude/skills/` |
| Gemini CLI | `.gemini/skills/ia-skill_mi-memoria/` | `~/.gemini/skills/` |
| Otros agentes | revisar convención del agente | revisar convención del agente |

Para que un agente reconozca la habilidad, el archivo `SKILL.md` debe quedar en la raíz de la carpeta del skill.

## Capacidades actuales v0.4.2

La fuente operativa para capacidades actuales es:

```bash
./bin/mi-memoria capabilities --json
```

En conversaciones con Codex, `/mem` es alias corto de `/mi-memoria`. El binario local se mantiene como `mi-memoria`.

En v0.4 el runtime expone:

- `capture`: captura ideas/notas rápidas con `--kind`/`--type` y destino controlado opcional (`--to`).
- `daily`: crea/actualiza notas diarias minimalistas con append y resumen.
- `decision`: registra decisiones trazables (`new`, `from-session`, `list`) con `decision_status`.
- `classify`: propone destino taxonómico (`00/10/20/30/40`) con racional y alternativas.
- `review`: genera reportes de calidad estructural en `.md` y `.json`.
- `link`: sugiere wikilinks candidatos sin persistir cambios automáticamente.
- `summarize`: sintetiza nota/carpeta con trazabilidad de fuentes.
- `normalize`: normaliza Markdown libre hacia una nota Obsidian consistente.
- `validate`: valida frontmatter, secciones mínimas y nombre de archivo.
- `remember`: registra memoria curada y resumida en `memory/` del vault por defecto (`remember+` con `--type`).
- `index`: construye índices navegables y reportes de duplicados sin mutar notas.
- `timeline`: construye línea de tiempo trazable con fechas explícitas o inferidas.
- `drift-detection`: detecta deriva estructural/taxonómica y emite reportes `.md` + `.json`.
- `curate`: propone planes de curaduría y reportes sin ejecutar cambios masivos.
- `publish`: exporta subconjuntos de conocimiento sin mutar fuentes (`--format markdown`, `--context-pack`).
- `archive`: ejecuta archivado gobernado en `40-archive/` con `--preview|--apply`.
- `query`: consulta contextual local con evidencia, inferencia e incertidumbre explícitas.
- `context-build`: construye paquetes de contexto acotados con `context-pack` y `source-map`.
- `session`: gestiona sesiones temporales (`start/add/context/close`) sin persistencia automática.
- `template`: lista, muestra, genera, valida y aplica plantillas Markdown.
- `apply`: aplica un preview validado desde el workspace del runtime o del vault hacia un destino final del vault.
- `ask`: detecta intenciones simples de normalización desde lenguaje natural.
- `context`: reporta runtime, workspace técnico, vault configurado, workspace visible e idioma.
- `capabilities`: lista capacidades, comandos, tipos, estados y destinos soportados.
- `capabilities`: también expone `version` y `maturity` operativa.
- `upgrade`: actualiza el runtime del skill con `git pull --ff-only`.

## Capacidades planeadas

La revisión documental contra master-plan está propuesta para evolución futura. Incluye ideas como `review-docs`, `align-readme` y `review-master-plan`, pero esos comandos no existen en v0.1 y no deben tratarse como funcionalidad implementada.

El objetivo futuro es generar planes o reportes de alineación documental que distingan capacidades reales, gaps, documentación obsoleta y decisiones diferidas.

Nota de gobernanza de versiones y releases: ver `AGENTS.md` (sección de release, tag y backport).

## Uso rápido

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria capture --kind idea --text "Idea rápida"
./bin/mi-memoria daily --append "Nota rápida"
./bin/mi-memoria decision new --title "Separar runtime y vault" --decision-status accepted --json
./bin/mi-memoria classify --input workspace/inbox/2026-05-08-idea.md --json
./bin/mi-memoria review --path workspace/inbox --json
./bin/mi-memoria link --input workspace/inbox/2026-05-08-idea.md --preview --json
./bin/mi-memoria summarize --path workspace/inbox --json
./bin/mi-memoria index --path workspace/inbox --json
./bin/mi-memoria timeline --path workspace/inbox --json
./bin/mi-memoria drift-detection --path workspace/inbox --json
./bin/mi-memoria curate --path workspace/inbox --json
./bin/mi-memoria publish --path workspace/inbox --output workspace/exports/pack --format markdown --json
./bin/mi-memoria publish --context-pack workspace/exports/2026-05-10-context-pack.json --output workspace/exports/pack-context --json
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria validate --input workspace/preview/2026-05-08-nota.md
./bin/mi-memoria template generate --name log-diario --type note --description "Registro diario de eventos" --preview
./bin/mi-memoria apply --input workspace/preview/2026-05-08-nota.md --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria remember --summary "Se adopta Python estándar para v0.1." --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria remember --type decision --summary "Se archiva por política explícita." --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria archive --input 30-resources/2026-05-10-nota.md --preview --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria upgrade --json
```

También puede configurarse el vault por entorno:

```bash
export MI_MEMORIA_VAULT_PATH=/path/to/mi-memoria-vault
```

Con el vault configurado, `remember` escribe por defecto en `memory/` del vault. La memoria interna del runtime solo debe usarse para comportamiento operacional del skill:

```bash
./bin/mi-memoria remember --summary "Convención interna del skill." --scope runtime
```

Las plantillas del vault tienen prioridad. Si falta una plantilla primitiva del vault, el runtime usa la plantilla CORE de `skills/core/templates` y emite un warning recomendando restaurarla con `scripts/skill_setup.sh` o crear una plantilla propia.

`template generate` crea previews en `workspace/preview/templates`. `template apply` copia esos previews a `vault/templates` solo si el destino no existe. `template sync` sincroniza faltantes CORE al vault en modo seguro y reporta diferencias sin sobrescribir.

`capabilities --json` expone metadata por comando para agentes. La fuente canónica es `skill-manifest.json` (raíz) y se mantiene un espejo idéntico en `docs/skill-manifest.json` por compatibilidad transitoria.

## Documentación de usuario

La documentación curada de usuario vive en el vault del proyecto, dentro de `docs/30-resources/mi-memoria/`. Ese hub es la referencia principal para uso, manifiestos, flujos y resolución de problemas.

- [Hub de documentación de usuario](docs/30-resources/mi-memoria/index.md)
- [Gobernanza documental](docs/documentation-governance.md)
- [Memoria curada del vault](docs/memory/README.md)
- [Taxonomía documental](docs/memory/conventions/documentation-taxonomy.md)

## P5 readiness (aún no ejecutada)

P5 (interoperabilidad controlada) sigue diferida. En `v0.4.2` no existe bridge MCP ni servidor HTTPS activo.

Gates previos obligatorios para iniciar P5:

- mantener CLI-first como contrato primario;
- exponer solo capacidades read-only en primera etapa;
- no ampliar permisos respecto a CLI local;
- mantener pruebas offline completas y mocks;
- bloquear por defecto operaciones destructivas remotas.

## Inicializar un vault

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
```

El script crea la estructura mínima y copia las plantillas CORE `note`, `memory` y `log` sin sobrescribir archivos existentes. Puede volver a ejecutarse sobre un vault existente para agregar plantillas faltantes.

El vault incluye un `workspace/` visible desde Obsidian con `inbox`, `processing`, `preview` y `exports`. Esa zona es para curaduría y edición puntual; no contiene scripts, logs, dependencias ni lógica operacional del runtime.

## Actualizar el skill

Si `mi-memoria` está instalado desde Git, puedes actualizar el componente del skill con:

```bash
./bin/mi-memoria upgrade
```

El comando está acotado al runtime actual y ejecuta únicamente:

```bash
git -C <runtime-mi-memoria> pull --ff-only
```

No escribe en el vault, no modifica memoria persistente y no acepta comandos arbitrarios. Si la actualización requiere merge, rebase o resolución de conflictos, falla y deja la decisión al usuario.

## Pruebas

```bash
make test
```

La implementación usa solo librería estándar de Python.
