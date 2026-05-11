---
title: "Plan de iteración documental"
type: memory
status: active
created: 2026-05-11
updated: 2026-05-11
tags: [mi-memoria, documentation, plan, iteration]
---

# Plan de iteración documental

## Memoria

Este plan convierte la experiencia de estabilización del corpus documental en una ruta de trabajo reutilizable para futuras versiones del skill.

## Resumen

La regla es simple:

- primero estabilizar el contrato;
- luego enriquecer la explicación de uso;
- después curar las ideas que salieron de la práctica;
- finalmente promover esas ideas a la siguiente iteración del repo.

## Desarrollo

### Ideas derivadas de la experiencia

- Mantener `prompt` para activación conversacional y `bash` para comandos técnicos.
- Separar siempre documentación de usuario, gobernanza y memoria curada.
- Mantener `README.md` y `SKILL.md` como puntos de entrada alineados.
- Usar `capabilities --json` y `skill-manifest.json` como contrato visible, no como narrativa.
- Tratar `CHANGELOG.md` como evidencia de madurez, no solo como historial.
- Expandir primero `commands.md`, `manifests.md`, `overview.md`, `workflows.md` y `quickstart.md` cuando cambie el contrato de uso.
- Añadir ejemplos reales antes de inventar nuevas secciones.
- No mover contenido al vault final sin preview, validación y relación explícita.

### Secuencia recomendada por iteración

1. Capturar la convención o idea.
2. Curarla en memoria del vault.
3. Registrar una nota runtime breve.
4. Aplicar el cambio a la documentación visible.
5. Validar el repositorio.
6. Marcar el cambio en `CHANGELOG.md`.
7. Promover solo si el contrato quedó estable.

### Dónde se aplica

- `docs/30-resources/mi-memoria/` para documentación de usuario.
- `docs/memory/conventions/` para ideas, reglas y planes de iteración.
- `memory/hot/` para aprendizaje operacional del skill.
- `README.md` y `SKILL.md` para entrada oficial del repositorio.

## Relaciones

- [convención de estilo editorial](editorial-style.md)
- [taxonomía documental](documentation-taxonomy.md)
- [memoria README](../README.md)
- [documentación de usuario](../../30-resources/mi-memoria/index.md)

## Pendientes

- Convertir las ideas de iteración en tareas concretas cuando aparezca una nueva release.
- Mantener el plan vivo a medida que cambie `capabilities --json`.
