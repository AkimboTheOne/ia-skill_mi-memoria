# Activación

## Slash command conceptual

```text
/mi-memoria normalize
/mi-memoria remember
/mi-memoria validate
```

## CLI local

```bash
./bin/mi-memoria run normalize --input note.md --preview
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/vault
./bin/mi-memoria validate --input note.md
./bin/mi-memoria remember --summary "..."
```

## Lenguaje natural

`ask` detecta intenciones simples de normalización y genera un preview:

```bash
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
```

Si `MI_MEMORIA_VAULT_PATH` está configurado, `ask` genera el preview en `vault/workspace/preview` para revisión desde Obsidian. Sin vault configurado, usa el workspace técnico del runtime.
