# Sub-Charter P3 v0.1 — Inteligencia Contextual Local de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Fase | P3 |
| Nombre | Inteligencia Contextual Local |
| Estado | Propuesta para planificación Codex |
| Dependencias | P1 y P2 estabilizados |

---

# 1. Propósito

P3 introduce capacidades de consulta y construcción de contexto local.

Esta fase NO introduce aún interoperabilidad externa.

El objetivo es permitir que `mi-memoria` prepare contexto útil para humanos y agentes sin cargar el vault completo ni depender de infraestructura externa.

---

# 2. Features Incluidas

| ID | Feature | Propósito |
|---|---|---|
| F11 | `query` | Consulta contextual local |
| F12 | `context-build` | Construcción de paquetes de contexto |
| F13 | `session` | Gestión de sesiones temporales de trabajo |

---

# 3. Feature F11 — `query`

## Responsabilidad

Consultar el vault local mediante búsqueda estructurada y asistencia LLM.

## Activación

```text
/mi-memoria query
```

## CLI Esperada

```bash
mi-memoria query "decisiones sobre taxonomía"
mi-memoria query "runtime separado del vault" --path context
mi-memoria query "normalización markdown" --json
```

## Runtime

Debe:

- limitar alcance;
- buscar en nombres, títulos, tags y contenido;
- retornar archivos fuente;
- distinguir resultado exacto de inferencia;
- evitar respuestas sin evidencia.

## LLM

Puede:

- sintetizar resultados;
- explicar relaciones;
- formular respuesta contextual;
- señalar incertidumbre.

## Regla

Toda respuesta debe estar trazada a notas o archivos fuente.

Si no hay evidencia suficiente, debe decirlo.

---

# 4. Feature F12 — `context-build`

## Responsabilidad

Construir paquetes de contexto para humanos, Codex u otros agentes.

## Activación

```text
/mi-memoria context-build
```

## CLI Esperada

```bash
mi-memoria context-build --topic mi-memoria-runtime
mi-memoria context-build --path 20-projects/mi-memoria --output workspace/exports/context-pack.md
mi-memoria context-build --topic "taxonomía" --format json
```

## Runtime

Debe:

- seleccionar archivos fuente;
- limitar tamaño;
- generar índice de fuentes;
- registrar criterios de selección;
- producir artefacto reutilizable.

## LLM

Puede:

- resumir;
- ordenar;
- reducir redundancia;
- estructurar contexto para consumo de agentes.

## Salidas Esperadas

```text
context-pack.md
context-pack.json
source-map.json
```

---

# 5. Feature F13 — `session`

## Responsabilidad

Crear sesiones temporales de trabajo con alcance controlado.

## Activación

```text
/mi-memoria session
```

## CLI Esperada

```bash
mi-memoria session start --name arquitectura-mi-memoria
mi-memoria session add --input note.md
mi-memoria session context --json
mi-memoria session close --remember
```

## Runtime

Debe:

- registrar sesión;
- mantener archivos activos;
- generar contexto acotado;
- cerrar sesión con resumen opcional;
- no persistir memoria sin aprobación.

## LLM

Puede:

- resumir sesión;
- proponer decisiones;
- identificar pendientes;
- sugerir memoria curada.

## Regla

La sesión es transitoria. Solo se vuelve memoria si el usuario aprueba `remember`.

---

# 6. Relación con `$VAULT/context/`

P3 puede leer `$VAULT/context/` como fuente de gobernanza y metaconocimiento.

Debe usarlo para:

- principios;
- decisiones;
- convenciones;
- resúmenes consolidados.

No debe llenar `$VAULT/context/` con dumps de consulta.

---

# 7. Entregables Codex

Codex debe generar plan para:

- búsqueda local básica;
- contratos de resultados;
- formato de context packs;
- lifecycle de sesiones;
- validación de evidencia;
- tests con vault de ejemplo;
- documentación de uso.

---

# 8. Criterios de Aceptación P3

P3 se acepta cuando:

- `query` responde con fuentes trazables;
- `context-build` genera paquetes acotados;
- `session` controla alcance temporal;
- no hay dependencia externa obligatoria;
- las respuestas distinguen evidencia, inferencia e incertidumbre;
- se evita cargar todo el vault sin necesidad.

---

# 9. Revisión de Consistencia

P3 es consistente porque:

- aprovecha P1 y P2;
- mantiene operación local;
- no introduce MCP ni HTTPS;
- preserva el LLM como asistente;
- fortalece el uso de contexto sin convertirlo en memoria indiscriminada.
