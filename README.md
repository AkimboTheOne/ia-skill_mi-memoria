# mi-memoria

Runtime local de skills para operar sobre repositorios de conocimiento Markdown, separado del vault de conocimiento.

`mi-memoria` v0.1 implementa una baseline mínima:

- CLI local sin dependencias externas obligatorias.
- Skill `normalize` para convertir texto o Markdown libre en notas Obsidian consistentes.
- Validación de estructura, frontmatter, nombres y secciones mínimas.
- Workspace transitorio con preview seguro.
- Escritura controlada hacia un vault externo.
- Memoria operacional curada mediante `remember`.
- Setup inicial de vault mediante `scripts/skill_setup.sh`.
- Actualización segura del runtime mediante `upgrade`.

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

## Capacidades actuales v0.1

La fuente operativa para capacidades actuales es:

```bash
./bin/mi-memoria capabilities --json
```

En v0.1 el runtime expone:

- `normalize`: normaliza Markdown libre hacia una nota Obsidian consistente.
- `validate`: valida frontmatter, secciones mínimas y nombre de archivo.
- `remember`: registra memoria operacional curada y resumida.
- `apply`: aplica un preview validado hacia un vault externo.
- `ask`: detecta intenciones simples de normalización desde lenguaje natural.
- `context`: reporta runtime, workspace, vault configurado e idioma.
- `capabilities`: lista capacidades, comandos, tipos, estados y destinos soportados.
- `upgrade`: actualiza el runtime del skill con `git pull --ff-only`.

## Capacidades planeadas

La revisión documental contra master-plan está propuesta para evolución futura. Incluye ideas como `review-docs`, `align-readme` y `review-master-plan`, pero esos comandos no existen en v0.1 y no deben tratarse como funcionalidad implementada.

El objetivo futuro es generar planes o reportes de alineación documental que distingan capacidades reales, gaps, documentación obsoleta y decisiones diferidas.

## Uso rápido

```bash
./bin/mi-memoria capabilities --json
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input workspace/preview/2026-05-08-nota.md
./bin/mi-memoria apply --input workspace/preview/2026-05-08-nota.md --vault-path /path/to/mi-memoria-vault
./bin/mi-memoria remember --summary "Se adopta Python estándar para v0.1."
./bin/mi-memoria upgrade --json
```

También puede configurarse el vault por entorno:

```bash
export MI_MEMORIA_VAULT_PATH=/path/to/mi-memoria-vault
```

## Inicializar un vault

```bash
./scripts/skill_setup.sh /path/to/mi-memoria-vault
```

El script crea la estructura mínima sin sobrescribir archivos existentes.

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
