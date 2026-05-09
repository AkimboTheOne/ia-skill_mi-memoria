# Gobernanza Documental

La documentación de `mi-memoria` es un artefacto operacional. Debe describir el comportamiento verificable del runtime y separar con claridad lo implementado, lo propuesto y lo diferido.

## Fuentes autoritativas

- `mi-memoria-charter-baseline-v0.1.md`: propósito, arquitectura base, límites y evolución esperada.
- `AGENTS.md`: principios operacionales y límites obligatorios de v0.1.
- `SKILL.md`: activación y contrato de uso del runtime.
- `docs/`: explicación operacional de arquitectura, uso, validación, activación y scope.
- `harnesses/`: restricciones, límites de comportamiento y checks de aceptación.
- `./bin/mi-memoria capabilities --json`: fuente ejecutable para capacidades actuales.
- `tests/`: evidencia automatizada del comportamiento implementado.

## Reglas de alineación

- Una capacidad solo puede documentarse como actual si aparece en `capabilities --json` o está cubierta por pruebas y comandos existentes.
- Las capacidades futuras deben marcarse explícitamente como `planeadas`, `diferidas`, `roadmap` o `propuestas`.
- La documentación no debe inventar arquitectura, comandos, APIs, servicios externos ni automatización no implementada.
- Las actualizaciones deben preservar la separación entre runtime y vault externo.
- La documentación debe priorizar precisión operacional sobre narrativa promocional.

## Estado de `review-docs`

La revisión documental contra master-plan es una capacidad propuesta. El subcharter externo de `review-docs` sirve como insumo de gobernanza, pero no prueba implementación.

En v0.1 no existen comandos como:

```text
/mi-memoria review-docs
/mi-memoria align-readme
/mi-memoria review-master-plan
```

Hasta que exista implementación, pruebas y exposición en `capabilities --json`, esos nombres deben aparecer solamente como roadmap o diferidos.

## Check mínimo antes de publicar cambios documentales

```bash
./bin/mi-memoria capabilities --json
make test
rg -n "review-docs|align-readme|review-master-plan" README.md SKILL.md docs harnesses
```

El resultado esperado es que las capacidades actuales coincidan con el CLI y que cualquier referencia a capacidades futuras esté marcada como propuesta, diferida o roadmap.
