# Gobierno de Scope

## Incluido en v0.1

- CLI local.
- Normalización Markdown.
- Preview seguro.
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

## Roadmap documental

La revisión documental es una línea de evolución futura orientada a gobernanza. En v0.1 puede documentarse como propuesta, pero no como comando disponible.

Antes de moverla a alcance implementado debe existir:

- comando o skill ejecutable;
- exposición en `./bin/mi-memoria capabilities --json`;
- pruebas automatizadas;
- actualización de `README.md`, `SKILL.md`, `docs/` y `harnesses/`.
