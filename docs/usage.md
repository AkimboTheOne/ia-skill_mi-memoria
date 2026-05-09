# Uso

## Normalizar con preview

```bash
./bin/mi-memoria run normalize --input note.md --preview
```

Sin vault configurado, el preview queda en `runtime/workspace/preview`.

## Normalizar con preview visible en Obsidian

```bash
./bin/mi-memoria run normalize --input note.md --preview --vault-path /path/to/vault
```

Con `--vault-path` o `MI_MEMORIA_VAULT_PATH`, el preview queda en `vault/workspace/preview`.

## Escribir al vault

```bash
./bin/mi-memoria run normalize --input note.md --write --vault-path /path/to/vault
```

## Aplicar un preview

```bash
./bin/mi-memoria apply --input workspace/preview/archivo.md --vault-path /path/to/vault
```

`apply` acepta previews desde `runtime/workspace/preview` o desde `vault/workspace/preview`.

## Validar

```bash
./bin/mi-memoria validate --input archivo.md --json
```

## Memoria

```bash
./bin/mi-memoria remember --summary "Convención aprobada: usar estado draft por defecto."
```
