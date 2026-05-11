---
title: "Proyecto de convenciones documentales"
type: project
status: active
created: 2026-05-11
updated: 2026-05-11
tags: [mi-memoria, project, documentation, conventions]
aliases: [convenciones documentales, proyecto de documentación]
---

# Proyecto de convenciones documentales

## Resumen

Este proyecto recoge la experiencia de estabilizar la documentación del skill, del vault y de sus puntos de entrada.

Sirve para que un agente de codificación pueda entender:

- qué ya está estabilizado;
- qué cambió para reducir ambigüedad;
- qué piezas deben seguir vivas como referencia;
- qué archivos tocar primero para mejorar el skill sin romper el contrato.

## Contexto

El trabajo nació para resolver un patrón repetido:

- documentación dispersa;
- mezcla entre uso, gobernanza y memoria;
- activaciones con estilos distintos;
- poca trazabilidad entre contrato técnico, explicación de uso y memoria curada;
- riesgo de derivar en docs bonitas pero no operables.

## Lectura para agentes

### Orden recomendado

1. [Documentación de usuario](../30-resources/mi-memoria/index.md)
2. [Gobernanza documental](../documentation-governance.md)
3. [Convención de taxonomía documental](../memory/conventions/documentation-taxonomy.md)
4. [Convención de estilo editorial](../memory/conventions/editorial-style.md)
5. [Plan de iteración documental](../memory/conventions/documentation-iteration-plan.md)
6. [README.md](../../README.md)
7. [SKILL.md](../../SKILL.md)
8. [CHANGELOG.md](../../CHANGELOG.md)

### Qué debe inferir el agente

- `prompt` es activación conversacional o intención de usuario.
- `bash` es ejecución técnica real.
- `docs/30-resources/` contiene la guía de uso y referencia.
- `docs/memory/` contiene criterio, decisiones y convenciones.
- `docs/20-projects/` contiene trabajos vivos que todavía evolucionan.
- `capabilities --json` y `skill-manifest.json` son el contrato visible.
- `CHANGELOG.md` registra la evolución funcional y documental.

### Qué no debe asumir el agente

- Que una nota de memoria equivale a una implementación.
- Que un archivo de docs de usuario puede inventar comandos no expuestos.
- Que una convención ya está estabilizada solo porque se escribió una vez.
- Que el vault define el runtime.
- Que el README raíz puede tocarse sin revisar primero la documentación de usuario y la gobernanza.

## Objetivo

Mantener consistencia entre:

- activación conversacional en `prompt`;
- comandos técnicos en `bash`;
- documentación de usuario;
- gobernanza documental;
- memoria curada;
- README y SKILL como puntos de entrada;
- manifest y capacidades como contrato visible.

## Alcance

Incluye:

- [docs/30-resources/mi-memoria/](../30-resources/mi-memoria/index.md);
- [docs/memory/conventions/](../memory/conventions/README.md);
- [docs/documentation-governance.md](../documentation-governance.md);
- [docs/activation.md](../activation.md);
- [README.md](../../README.md);
- [SKILL.md](../../SKILL.md);
- [CHANGELOG.md](../../CHANGELOG.md).

## Estado actual

El proyecto ya incorporó:

- la distinción `prompt`/`bash`;
- la convención editorial de sentence case;
- la taxonomía documental;
- un plan de iteración documental;
- una expansión práctica del hub de usuario;
- una capa de trazabilidad entre memoria curada y proyecto vivo.

## Experiencia recaudada

### Lo que funcionó

- Separar `prompt` de `bash` reduce ambigüedad para usuarios y agentes.
- Expandir primero el hub de usuario acelera la comprensión del skill.
- Registrar la convención editorial en vault y runtime evita que la regla viva solo en la conversación.
- Mantener `README.md`, `SKILL.md` y gobernanza alineados reduce deriva en los puntos de entrada.
- Usar `CHANGELOG.md` como evento de documentación deja evidencia de evolución real.
- Convertir la convención en proyecto hace visible el trabajo vivo y evita que se pierda entre memorias sueltas.

### Señales de calidad

- Los títulos visibles siguen sentence case salvo semántica técnica.
- La activación conversacional se lee como intención, no como comando de shell.
- El binario local conserva el contrato técnico verificable.
- El hub de usuario explica el uso antes que la implementación.
- La memoria curada contiene criterio; el proyecto contiene trabajo vivo.
- Los archivos enlazados tienen una función distinta y complementaria.

### Riesgos evitados

- Mezclar prompt con bash en la documentación pública.
- Publicar contratos no implementados como si fueran actuales.
- Dejar la documentación de usuario separada del contrato real del CLI.
- Encerrar la convención editorial dentro de una nota aislada sin ruta de iteración.
- Perder trazabilidad entre decisiones de gobernanza y cambios visibles en el repo.
- Tratar un proyecto vivo como memoria muerta.

### Decisiones asentadas

- `docs/30-resources/mi-memoria/` es el hub de usuario.
- `docs/memory/` es la capa de memoria y gobernanza.
- `docs/20-projects/documentation-conventions.md` es el registro vivo del trabajo de estabilización.
- `prompt` se usa para activación conversacional.
- `bash` se usa para ejecución técnica.
- Sentence case es la convención editorial por defecto.
- `CHANGELOG.md` debe registrar cambios documentales relevantes.

### Superficies de cambio para mejorar el skill

Para un agente de codificación, los primeros lugares a revisar son:

- `docs/30-resources/mi-memoria/commands.md`: ejemplos de uso y contrato de comandos.
- `docs/30-resources/mi-memoria/manifests.md`: lectura del manifiesto y del binario.
- `docs/30-resources/mi-memoria/quickstart.md`: onboarding y activación mínima.
- `docs/30-resources/mi-memoria/overview.md`: mapa conceptual del runtime.
- `docs/30-resources/mi-memoria/workflows.md`: secuencias de trabajo.
- `docs/memory/conventions/editorial-style.md`: reglas editoriales reutilizables.
- `docs/memory/conventions/documentation-iteration-plan.md`: ruta para convertir experiencia en nuevas iteraciones.
- `docs/documentation-governance.md`: límites y criterios de alineación.
- `README.md` y `SKILL.md`: entradas oficiales del repositorio.
- `skill-manifest.json`: contrato canónico que debe reflejar `capabilities --json`.

### Aprendizaje operativo

- Primero cambia la explicación de uso, luego ajusta el contrato visible.
- Si cambias un patrón editorial, propágalo a vault y runtime.
- Si agregas una convención, también agrega la ruta donde un agente la puede reutilizar.
- Si cambias la documentación de usuario, registra el evento en `CHANGELOG.md`.
- Si una nueva pieza no ayuda a un agente a tomar acción, probablemente todavía no está lista.

## Artefactos generados

- [documentación de usuario](../30-resources/mi-memoria/index.md)
- [gobernanza documental](../documentation-governance.md)
- [taxonomía documental](../memory/conventions/documentation-taxonomy.md)
- [estilo editorial](../memory/conventions/editorial-style.md)
- [plan de iteración documental](../memory/conventions/documentation-iteration-plan.md)
- [memoria runtime del plan](../../memory/hot/2026-05-11-plan-de-iteracion-documental.md)

## Relaciones

- [Convención de taxonomía documental](../memory/conventions/documentation-taxonomy.md)
- [Convención de estilo editorial](../memory/conventions/editorial-style.md)
- [Plan de iteración documental](../memory/conventions/documentation-iteration-plan.md)
- [Documentación de usuario](../30-resources/mi-memoria/index.md)
- [Memoria curada](../memory/README.md)

## Siguiente paso

Convertir las ideas de iteración en tareas por release y mantener el proyecto visible hasta que el corpus se estabilice de forma durable.

### Ruta recomendada

1. Cerrar la siguiente revisión de docs de usuario.
2. Convertir observaciones nuevas en notas de memoria.
3. Promover solo lo que ya tenga evidencia de uso.
4. Mantener el proyecto vivo hasta que la convención deje de moverse.
5. Archivar cuando la evolución pase de diseño a mantenimiento.

## Checklist de intervención

Cuando un agente de codificación tome este proyecto como punto de partida, debería recorrer esta lista antes de cambiar archivos:

### 1. Entender el estado

- Leer [documentación de usuario](../30-resources/mi-memoria/index.md).
- Leer [gobernanza documental](../documentation-governance.md).
- Leer [convención de taxonomía documental](../memory/conventions/documentation-taxonomy.md).
- Leer [convención de estilo editorial](../memory/conventions/editorial-style.md).
- Leer [plan de iteración documental](../memory/conventions/documentation-iteration-plan.md).
- Revisar `README.md`, `SKILL.md` y `CHANGELOG.md`.

### 2. Identificar la superficie correcta

- Si el problema es uso o navegación, tocar primero `docs/30-resources/mi-memoria/`.
- Si el problema es criterio o gobernanza, tocar `docs/memory/`.
- Si el problema es explicación del contrato, tocar `README.md`, `SKILL.md` o `docs/documentation-governance.md`.
- Si el problema es activación o flujo técnico, tocar `docs/activation.md` o `docs/usage.md`.
- Si el problema es consistencia editorial, tocar la convención editorial y propagarla.

### 3. Aplicar cambios con cautela

- Mantener `prompt` para activación conversacional.
- Mantener `bash` para ejecución técnica.
- No inventar comandos nuevos.
- No marcar como actual lo que solo es propuesta.
- No mover contenido al vault final sin preview y validación.

### 4. Registrar aprendizaje

- Si surge una regla útil, llevarla a `docs/memory/conventions/`.
- Si la regla afecta comportamiento del skill, registrar también una memoria runtime.
- Si el cambio altera la documentación visible, anotarlo en `CHANGELOG.md`.
- Si el cambio introduce una nueva ruta de trabajo, actualizar el proyecto y su checklist.

### 5. Verificar salida

- Correr `make test`.
- Validar las notas de memoria nuevas.
- Confirmar que `capabilities --json` sigue alineado con el contrato visible.
- Revisar que el README y el SKILL no quedaron desalineados con la documentación de usuario.

### 6. Decidir cierre

- Si el cambio estabiliza una convención, mantener el proyecto vivo para iteraciones futuras.
- Si el cambio solo corrige una deriva puntual, dejar la nota como evidencia y seguir.
- Si el corpus ya no cambia, archivar el proyecto o moverlo a mantenimiento.

## Notas para agentes

- Este proyecto no es un destino final; es un punto de trabajo.
- Se puede usar como briefing de entrada para una tarea de mejora.
- Debe leerse junto con la memoria curada y no reemplaza el contrato del CLI.
- Si una decisión contradice `capabilities --json`, el contrato ejecutable manda.
