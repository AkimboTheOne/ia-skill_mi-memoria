# Gobernanza documental

La documentación de `mi-memoria` es un artefacto operacional. Debe describir el comportamiento verificable del runtime y separar con claridad lo implementado, lo propuesto y lo diferido.

## Fuentes autoritativas

- [charter baseline](memory/roadmap/charter-baseline.md): propósito, arquitectura base, límites y evolución esperada.
- [AGENTS.md](../AGENTS.md): principios operacionales y límites obligatorios de v0.1.
- [SKILL.md](../SKILL.md): activación y contrato de uso del runtime.
- [docs/30-resources/mi-memoria](30-resources/mi-memoria/index.md): explicación operacional de uso, validación, activación y scope de usuario.
- [docs/memory/roadmap](memory/roadmap/README.md): corpus curado de la evolución y gobernanza histórica.
- [harnesses/](../harnesses/): restricciones, límites de comportamiento y checks de aceptación.
- `./bin/mi-memoria capabilities --json`: fuente ejecutable para capacidades actuales.
- [tests/](../tests/): evidencia automatizada del comportamiento implementado.

## Reglas de alineación

- Una capacidad solo puede documentarse como actual si aparece en `capabilities --json` o está cubierta por pruebas y comandos existentes.
- Las capacidades futuras deben marcarse explícitamente como `planeadas`, `diferidas`, `roadmap` o `propuestas`.
- La documentación no debe inventar arquitectura, comandos, APIs, servicios externos ni automatización no implementada.
- Las actualizaciones deben preservar la separación entre runtime y vault externo.
- La documentación debe priorizar precisión operacional sobre narrativa promocional.

## Taxonomía documental

- [docs/memory/](memory/): contiene memoria curada, convenciones y criterios de gobernanza.
- [docs/00-inbox/](00-inbox/), [docs/10-areas/](10-areas/), [docs/20-projects/](20-projects/), [docs/30-resources/](30-resources/) y [docs/40-archive/](40-archive/) son taxonomía del vault para contenido documental, operativo o de referencia.
- `docs/20-projects/` también puede alojar proyectos vivos de documentación y estabilización del skill, como el proyecto de convenciones documentales.
- La documentación de uso y referencia del skill o del proyecto suele vivir en `30-resources/`.
- La documentación de gobernanza, decisiones y racionales vive en `docs/memory/`.
- La documentación de usuario curada de `mi-memoria` vive en [docs/30-resources/mi-memoria/](30-resources/mi-memoria/index.md).

## Estilo editorial

- La convención editorial del vault vive en [docs/memory/conventions/editorial-style.md](memory/conventions/editorial-style.md).
- Usar sentence case por defecto en títulos, secciones y texto visible.
- Conservar mayúsculas solo cuando aporten semántica: nombres propios, siglas, acrónimos y fases `P1..P5`.
- Usar `¿qué es ...?` cuando la frase sea una pregunta real.

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

## Ver también

- [Documentación de usuario](30-resources/mi-memoria/index.md)
- [Memoria curada](memory/README.md)
- [Taxonomía documental](memory/conventions/documentation-taxonomy.md)
- [Estilo editorial](memory/conventions/editorial-style.md)
