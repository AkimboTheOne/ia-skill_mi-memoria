# Activación

## Instalación

Para Codex en un repo compartido, instala el skill como submódulo Git:

```bash
git submodule add https://github.com/AkimboTheOne/ia-skill_mi-memoria.git .agents/skills/ia-skill_mi-memoria
git submodule update --init --recursive
```

También puede instalarse como skill global de usuario en `~/.agents/skills/` o `~/.codex/skills/`, según la versión de Codex. En otros agentes, usa la convención equivalente: `.claude/skills/` para Claude, `.gemini/skills/` para Gemini CLI, o la carpeta de skills indicada por el agente.

En todos los casos, `SKILL.md` debe quedar en la raíz de la carpeta del skill.

## Slash command conceptual

```text
/mi-memoria normalize
/mi-memoria remember
/mi-memoria validate
```

## CLI local

```bash
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria validate --input note.md
./bin/mi-memoria remember --summary "..."
./bin/mi-memoria upgrade
```

`upgrade` actualiza el runtime del skill con `git -C <runtime> pull --ff-only`. No escribe en el vault ni acepta comandos arbitrarios.

## Lenguaje natural

`ask` detecta intenciones simples de normalización y genera un preview:

```bash
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
```
