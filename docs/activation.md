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
./bin/mi-memoria validate --input note.md
./bin/mi-memoria remember --summary "..." --vault-path /path/to/vault
```

## Lenguaje natural

`ask` detecta intenciones simples de normalización y genera un preview:

```bash
./bin/mi-memoria ask "Normaliza esta nota sobre arquitectura"
```
