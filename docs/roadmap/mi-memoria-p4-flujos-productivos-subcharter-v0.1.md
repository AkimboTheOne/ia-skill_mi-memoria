# Sub-Charter P4 v0.1 — Flujos Productivos de Conocimiento de `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Fase | P4 |
| Nombre | Flujos Productivos de Conocimiento |
| Estado | Propuesta para planificación Codex |
| Dependencias | P1, P2 y P3 estabilizados |

---

# 1. Propósito

P4 formaliza workflows productivos de uso cotidiano sobre el vault.

Estas features hacen que `mi-memoria` sea útil como sistema personal/familiar de conocimiento, sin convertirlo en una plataforma pesada.

P4 recoge las features identificadas como 16 a 20 en la conversación.

---

# 2. Features Incluidas

| ID | Feature | Propósito |
|---|---|---|
| F16 | `capture` avanzado | Captura rápida mejorada y multi-origen local |
| F17 | `daily` | Notas diarias minimalistas |
| F18 | `decision` | Registro formal de decisiones estilo ADR ligero |
| F19 | `curate` | Limpieza y mejora del vault |
| F20 | `publish` | Exportación controlada de subconjuntos de conocimiento |

---

# 3. Feature F16 — `capture` avanzado

## Responsabilidad

Evolucionar la captura rápida de P1 para soportar flujos más ricos sin perder control.

## Activación

```text
/mi-memoria capture
```

## CLI Esperada

```bash
mi-memoria capture --text "idea"
mi-memoria capture --type idea --text "..."
mi-memoria capture --type reference --input source.md
mi-memoria capture --to workspace/inbox --json
```

## Runtime

Debe:

- aceptar tipo de captura;
- aplicar template mínimo;
- generar archivo temporal;
- registrar fuente;
- evitar consolidación automática.

## LLM

Puede:

- expandir idea;
- convertir input crudo en nota inicial;
- sugerir tipo;
- proponer relaciones.

## Restricción

No debe convertir toda captura en nota final. La captura sigue siendo entrada.

---

# 4. Feature F17 — `daily`

## Responsabilidad

Crear y mantener notas diarias minimalistas.

## Activación

```text
/mi-memoria daily
```

## CLI Esperada

```bash
mi-memoria daily
mi-memoria daily --date 2026-05-08
mi-memoria daily --append "nota rápida"
mi-memoria daily --summary
```

## Runtime

Debe:

- crear nota diaria si no existe;
- usar template estable;
- evitar sobrescritura;
- registrar entradas con timestamps.

## LLM

Puede:

- resumir el día;
- extraer decisiones;
- detectar pendientes;
- proponer memoria curada.

## Regla

La nota diaria no debe convertirse en vertedero infinito. Debe facilitar captura y posterior curación.

---

# 5. Feature F18 — `decision`

## Responsabilidad

Registrar decisiones de forma explícita, trazable y reutilizable.

## Activación

```text
/mi-memoria decision
```

## CLI Esperada

```bash
mi-memoria decision new --title "Separar runtime y vault"
mi-memoria decision from-session --session arquitectura-mi-memoria
mi-memoria decision list
```

## Runtime

Debe:

- generar template de decisión;
- registrar estado;
- registrar fecha;
- registrar contexto;
- permitir superseded/deprecated si aplica.

## LLM

Puede:

- redactar decisión;
- resumir alternativas;
- explicar consecuencias;
- proponer relaciones.

## Template Sugerido

```md
---
title:
status: proposed | accepted | superseded | deprecated
date:
tags:
---

# Decisión

## Contexto

## Opciones consideradas

## Decisión tomada

## Consecuencias

## Referencias
```

---

# 6. Feature F19 — `curate`

## Responsabilidad

Detectar y proponer acciones de limpieza, mejora o consolidación del vault.

## Activación

```text
/mi-memoria curate
```

## CLI Esperada

```bash
mi-memoria curate --path 30-resources
mi-memoria curate --path 20-projects/mi-memoria --preview
mi-memoria curate --report workspace/preview/curation-report.md
```

## Runtime

Debe detectar:

- notas débiles;
- duplicados potenciales;
- tags redundantes;
- notas sin relación;
- contenido envejecido;
- estructura excesiva.

## LLM

Puede:

- sugerir fusiones;
- proponer mejoras;
- identificar redundancias semánticas;
- resumir acciones recomendadas.

## Regla

`curate` genera planes. No ejecuta cambios masivos automáticamente.

---

# 7. Feature F20 — `publish`

## Responsabilidad

Exportar subconjuntos de conocimiento a paquetes limpios.

## Activación

```text
/mi-memoria publish
```

## CLI Esperada

```bash
mi-memoria publish --path 20-projects/mi-memoria --output workspace/exports/mi-memoria-pack
mi-memoria publish --context-pack workspace/exports/context-pack.md
mi-memoria publish --format markdown
```

## Runtime

Debe:

- seleccionar fuentes;
- copiar o generar export;
- limpiar metadatos privados si se configura;
- producir manifest;
- evitar modificar originales.

## LLM

Puede:

- generar introducción;
- resumir paquete;
- ordenar contenido;
- sugerir omisiones.

## Salidas Esperadas

```text
workspace/exports/<package>/
  README.md
  manifest.json
  files/
```

---

# 8. Entregables Codex

Codex debe generar plan para:

- templates de daily y decision;
- evolución de capture;
- reportes de curate;
- contratos de publish;
- validaciones anti-sobrescritura;
- pruebas de integridad;
- documentación de workflows.

---

# 9. Criterios de Aceptación P4

P4 se acepta cuando:

- `capture` avanzado respeta workspace;
- `daily` crea notas controladas;
- `decision` genera registros trazables;
- `curate` produce planes, no cambios destructivos;
- `publish` exporta sin modificar fuentes;
- todas las operaciones tienen preview o manifest;
- se preserva separación runtime/vault.

---

# 10. Revisión de Consistencia

P4 es consistente porque:

- se apoya en capacidades estabilizadas;
- no introduce interoperabilidad todavía;
- mejora productividad sin ceder control;
- mantiene el conocimiento real en `$VAULT/00-40`;
- mantiene `$VAULT/context/` para metaconocimiento;
- evita automatización masiva silenciosa.
