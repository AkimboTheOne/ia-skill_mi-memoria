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

## Plantillas

```bash
./bin/mi-memoria template list --json
./bin/mi-memoria template show --name note --vault-path /path/to/vault
./bin/mi-memoria template generate --name log-diario --type note --description "Registro diario de eventos" --preview --json
./bin/mi-memoria template validate --input workspace/preview/templates/log-diario.md --json
./bin/mi-memoria template apply --input workspace/preview/templates/log-diario.md --vault-path /path/to/vault --json
```

`template generate` no escribe al vault. Genera previews en `workspace/preview/templates`. `template apply` requiere vault y no sobrescribe templates existentes.

## Memoria

```bash
./bin/mi-memoria remember --summary "Convención aprobada: usar estado draft por defecto." --vault-path /path/to/vault
```

`remember` guarda memoria curada en `memory/` del vault por defecto. También puede usar `MI_MEMORIA_VAULT_PATH`.

Si falta `vault/templates/memory.md`, el runtime usa la plantilla CORE y reporta un warning. Para restaurar plantillas base sin sobrescribir las propias:

```bash
./scripts/skill_setup.sh /path/to/vault
```

La memoria interna del runtime es una excepción explícita para modular o actualizar el comportamiento del skill:

```bash
./bin/mi-memoria remember --summary "Convención interna del skill." --scope runtime
```
