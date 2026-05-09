# Uso

## Normalizar con preview

```bash
./bin/mi-memoria run normalize --input note.md --preview
```

## Escribir al vault

```bash
./bin/mi-memoria run normalize --input note.md --write --vault-path /path/to/vault
```

## Aplicar un preview

```bash
./bin/mi-memoria apply --input workspace/preview/archivo.md --vault-path /path/to/vault
```

## Validar

```bash
./bin/mi-memoria validate --input archivo.md --json
```

## Memoria

```bash
./bin/mi-memoria remember --summary "Convención aprobada: usar estado draft por defecto."
```
