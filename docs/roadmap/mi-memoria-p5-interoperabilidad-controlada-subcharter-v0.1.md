# Sub-Charter P5 v0.1 — Interoperabilidad Controlada de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Fase | P5 |
| Nombre | Interoperabilidad Controlada |
| Estado | Propuesta diferida para planificación Codex |
| Dependencias | P1, P2, P3 y P4 estabilizados |

---

# 1. Propósito

P5 introduce interoperabilidad solo después de estabilizar el runtime local.

Esta fase debe permitir que otros agentes, procesos o herramientas consuman capacidades de `mi-memoria` sin romper la gobernanza del sistema.

Interoperabilidad no significa autonomía ilimitada.

Significa exposición controlada de capacidades maduras.

---

# 2. Features Incluidas

| ID | Feature | Propósito |
|---|---|---|
| F13 | MCP Bridge | Compatibilidad controlada con MCP |
| F14 | HTTPS Runtime | Mini-servidor local para capacidades maduras |
| F15 | External Providers | Integraciones externas desacopladas |

---

# 3. Feature F13 — MCP Bridge

## Responsabilidad

Exponer capacidades maduras de `mi-memoria` mediante un bridge compatible con MCP.

## Estado

Diferido hasta P5.

## Capacidades candidatas

Solo deberían exponerse capacidades no destructivas primero:

```text
context
capabilities
usage
examples
query
context-build
review
drift-detection
```

Capacidades de escritura deben requerir confirmación o estar deshabilitadas inicialmente.

## Prohibido inicialmente

- `apply` remoto sin confirmación;
- `archive` remoto con ejecución directa;
- modificación masiva;
- borrado;
- escritura fuera del vault configurado;
- exposición de secretos;
- exposición de rutas arbitrarias.

## Regla

El bridge MCP no debe ampliar permisos por encima de los permitidos por la CLI.

---

# 4. Feature F14 — HTTPS Runtime

## Responsabilidad

Exponer un mini-servidor local para discovery y ejecución controlada.

## Activación

```bash
mi-memoria serve --https --port 9443
```

## Endpoints Candidatos

```text
GET /health
GET /version
GET /context
GET /capabilities
GET /usage
GET /examples
GET /schema
POST /query
POST /context-build
POST /review
POST /validate
```

## Runtime

Debe:

- exigir configuración explícita;
- operar localmente por defecto;
- evitar exposición pública accidental;
- compartir contratos con CLI;
- registrar requests relevantes.

## Regla

La CLI sigue siendo el contrato operativo primario.

HTTPS es una capa adicional, no el núcleo del sistema.

---

# 5. Feature F15 — External Providers

## Responsabilidad

Permitir integraciones con terceros como servicios desacoplados.

## Posibles Proveedores

- GitHub;
- ADO;
- Jira;
- buscadores documentales;
- APIs internas;
- modelos LLM configurables;
- repositorios remotos.

## Estructura Esperada

```text
services/
  README.md
  <provider>/
    README.md
    config.example.yaml
    <provider>.env.example
    examples/
    mocks/
```

## Runtime

Debe:

- aislar cada proveedor;
- exigir configuración explícita;
- soportar mocks;
- validar permisos mínimos;
- no mezclar servicios en el core.

## Regla

Los servicios externos son extensiones. No deben ser prerequisito para operar el runtime local.

---

# 6. Seguridad P5

P5 debe ser tratada como fase de mayor riesgo.

Debe incluir:

- configuración explícita;
- allowlist de capacidades;
- logs;
- validación de rutas;
- control de permisos;
- no exposición de secretos;
- endpoints de solo lectura por defecto;
- mocks para pruebas offline.

---

# 7. Entregables Codex

Codex debe generar plan para:

- contratos MCP;
- contratos HTTP;
- schemas JSON;
- comandos `serve`;
- estrategia de seguridad local;
- mocks de servicios externos;
- pruebas offline;
- documentación de permisos;
- compatibilidad CLI-first.

---

# 8. Criterios de Aceptación P5

P5 se acepta cuando:

- MCP no amplía permisos;
- HTTPS es opcional;
- servicios externos son desacoplados;
- la CLI sigue funcionando sin red;
- existe discovery de capacidades;
- los endpoints tienen contratos;
- existen mocks;
- no hay secretos en logs;
- las operaciones destructivas están bloqueadas o requieren confirmación.

---

# 9. Revisión de Consistencia

P5 es consistente porque:

- se ubica al final;
- evita exponer capacidades inmaduras;
- conserva CLI como contrato primario;
- no vuelve obligatorio ningún servicio externo;
- mantiene seguridad por defecto;
- permite evolución estratégica sin contaminar el core.
