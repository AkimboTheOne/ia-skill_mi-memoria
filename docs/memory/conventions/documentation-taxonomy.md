---
title: "Convención de taxonomía documental"
type: memory
status: draft
created: 2026-05-10
updated: 2026-05-10
tags: [mi-memoria, memoria, convencion, taxonomy, documentation]
aliases: [taxonomia documental, convención de documentación]
source: "gobernanza-documental"
---

# Convención de Taxonomía Documental

## Memoria

La documentación del proyecto se divide en dos capas distintas:

- memoria curada del vault, para criterios, decisiones y racionales;
- taxonomía numerada del vault, para contenido documental de uso y referencia.

La convención es:

- `docs/memory/` guarda memoria curada, decisiones, convenciones y criterios de gobernanza;
- `docs/30-resources/` guarda documentación de uso, referencia, manuales y guías de consumo;
- `docs/10-areas/` guarda responsabilidades vivas y sostenidas;
- `docs/20-projects/` guarda documentación de trabajo con objetivo y cierre;
- `docs/40-archive/` guarda material cerrado o histórico;
- `docs/00-inbox/` guarda material sin clasificar.

## Regla De Clasificación

Usar `docs/memory/` cuando el documento responde a una pregunta de gobernanza:

- por qué el sistema se organizó así;
- qué convención gobierna la clasificación;
- qué criterio se aprobó;
- qué decisión histórica debe preservarse;
- qué racional explica la arquitectura.

Usar la taxonomía numerada cuando el documento responde a una pregunta de uso:

- cómo usar el skill;
- cómo instalar o activar el runtime;
- cómo consultar comandos;
- cómo ejecutar un flujo;
- cómo referenciar una capacidad.

## Consecuencia Práctica

La documentación del producto o del skill puede vivir en los numerales, normalmente en `30-resources/`, si su función es servir como referencia de usuario.

La documentación que explica el criterio de organización vive en `docs/memory/`.

## Trazabilidad

Esta convención se apoya en:

- [architecture](../../architecture.md)
- [scope governance](../../scope-governance.md)
- [documentation governance](../../documentation-governance.md)
- [roadmap curado](../roadmap/README.md)

## Ver también

- [documentación de usuario](../../30-resources/mi-memoria/index.md)
- [memoria README](../README.md)

## Lectura Operativa

Si el documento explica el sistema, va a memoria.

Si el documento explica cómo usar el sistema, va a recursos.
