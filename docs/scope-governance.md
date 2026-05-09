# Gobierno de Scope

## Incluido en v0.1

- CLI local.
- Normalización Markdown.
- Preview seguro.
- Workspace curatorial visible en el vault.
- Escritura explícita.
- Setup de vault externo.
- Memoria curada explícita.
- Validación mínima.

## Diferido

- Revisión documental automatizada contra master-plan (`review-docs`).
- Alineación automática de README o reportes de gaps documentales (`align-readme`, `review-master-plan`).
- MCP funcional.
- HTTPS.
- APIs externas.
- Vector DB.
- RAG.
- Agentes autónomos.
- Automatización masiva.

Toda expansión debe demostrar necesidad operacional, repetibilidad y reducción concreta de trabajo manual.

El workspace visible del vault pertenece al alcance v0.1 porque reduce desborde y caos durante curaduría manual en Obsidian sin introducir automatización adicional ni lógica operacional dentro del vault.

## Roadmap documental

La revisión documental es una línea de evolución futura orientada a gobernanza. En v0.1 puede documentarse como propuesta, pero no como comando disponible.

Antes de moverla a alcance implementado debe existir:

- comando o skill ejecutable;
- exposición en `./bin/mi-memoria capabilities --json`;
- pruebas automatizadas;
- actualización de `README.md`, `SKILL.md`, `docs/` y `harnesses/`.
