# Activación

## Instalación

Para Codex en un repo compartido, instala el skill como submódulo Git:

```bash
git submodule add https://github.com/AkimboTheOne/ia-skill_mi-memoria.git .agents/skills/ia-skill_mi-memoria
git submodule update --init --recursive
```

También puede instalarse como skill global de usuario en `~/.agents/skills/` o `~/.codex/skills/`, según la versión de Codex. En otros agentes, usa la convención equivalente: `.claude/skills/` para Claude, `.gemini/skills/` para Gemini CLI, o la carpeta de skills indicada por el agente.

En todos los casos, `SKILL.md` debe quedar en la raíz de la carpeta del skill.

## Activación en `prompt`

Usa este formato cuando estés en un agente conversacional o coding CLI que cargue el skill.

```prompt
/mi-memoria normalize
/mi-memoria remember
/mi-memoria validate
/mem normalize
/mem remember
/mem validate
```

```prompt
Organiza esta nota.
Normaliza esta idea antes de moverla.
Clasifica este Markdown.
Guarda esta decisión como memoria.
```

`/mem` es alias corto de `/mi-memoria`. Ambos activan el mismo runtime, las mismas reglas y las mismas capacidades; no existe un segundo CLI.

## Comandos técnicos en `bash`

```bash
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/vault
./bin/mi-memoria validate --input note.md
./bin/mi-memoria remember --summary "..." --vault-path /path/to/vault
./bin/mi-memoria upgrade
```

`upgrade` actualiza el runtime del skill con `git -C <runtime> pull --ff-only`. No escribe en el vault ni acepta comandos arbitrarios.

## Lenguaje natural

`ask` detecta intenciones simples de normalización y genera un preview:

```bash
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
```

Si `MI_MEMORIA_VAULT_PATH` está configurado, `ask` genera el preview en `vault/workspace/preview` para revisión desde Obsidian. Sin vault configurado, usa el workspace técnico del runtime.
