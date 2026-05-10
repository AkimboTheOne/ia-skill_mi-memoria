# Plan de Evolución Progresiva — `mi-memoria`

## Metadata

| Campo | Valor |
|---|---|
| Proyecto | `mi-memoria` |
| Tipo | Runtime local de skills para repositorios Markdown/Obsidian |
| Documento | Plan de evolución progresiva |
| Versión | `v0.1` |
| Fecha | 2026-05-08 |
| Estado | Propuesta aprobada para planificación Codex |
| Baseline origen | `mi-memoria-charter-baseline-v0.1.md` |

---

# 1. Propósito

Este documento define un set progresivo de features para evolucionar `mi-memoria` sin romper su baseline minimalista.

La evolución debe conservar los principios fundacionales:

- runtime separado del vault;
- vault como conocimiento persistente, no como runtime;
- workspace como zona transitoria;
- memoria reflexiva y curada;
- LLM asistente, no gobernante;
- operaciones verificables;
- escritura controlada;
- interoperabilidad diferida hasta que exista madurez operacional.

---

# 2. Regla Arquitectónica Principal

`mi-memoria` debe evolucionar por fases.

Cada fase debe:

- agregar capacidades coherentes;
- evitar mezclar responsabilidades;
- mantener compatibilidad CLI;
- producir salidas verificables;
- preservar seguridad operacional;
- poder ser implementada y probada por Codex de forma incremental.

No se deben introducir features de una fase superior si los prerequisitos de fases previas no están estabilizados.

---

# 3. Modelo Human-Governed / Runtime-Controlled / LLM-Assisted

Todas las features deben cumplir esta separación:

| Capa | Responsabilidad |
|---|---|
| Humano | Decide, aprueba, corrige, gobierna |
| Runtime | Estructura, valida, persiste, controla rutas y operaciones |
| LLM | Expande, resume, clasifica, sugiere, interpreta |

El LLM NO debe:

- mover archivos sin confirmación;
- modificar taxonomías globales sin aprobación;
- archivar conocimiento automáticamente;
- persistir memoria sin curación;
- crear relaciones permanentes sin validación.

---

# 4. Fases Progresivas

| Fase | Nombre | Propósito |
|---|---|---|
| P1 | Consolidación Operacional | Capturar, clasificar, revisar, enlazar y resumir |
| P2 | Gobernanza del Conocimiento | Indexar, trazar historia, detectar deriva y archivar |
| P3 | Inteligencia Contextual Local | Consultar, construir contexto y gestionar sesiones |
| P4 | Flujos Productivos de Conocimiento | Captura rápida, notas diarias, decisiones, curaduría y publicación |
| P5 | Interoperabilidad Controlada | MCP, HTTPS y proveedores externos desacoplados |

---

# 5. Orden Recomendado

## P1 primero
Porque fortalece la calidad operativa del vault sin introducir infraestructura externa.

## P2 después
Porque la gobernanza solo tiene sentido cuando ya existen notas, clasificaciones y enlaces suficientes.

## P3 después
Porque la consulta contextual requiere una base ordenada y revisada.

## P4 después
Porque los flujos productivos dependen de reglas maduras de captura, curación y publicación.

## P5 al final
Porque interoperar temprano expone contratos inmaduros, aumenta superficie de error y consolida deuda antes de tiempo.

---

# 6. Artefactos de Sub-Charter

Este plan se complementa con cinco sub-charters:

```text
mi-memoria-p1-consolidacion-operacional-subcharter-v0.1.md
mi-memoria-p2-gobernanza-conocimiento-subcharter-v0.1.md
mi-memoria-p3-inteligencia-contextual-subcharter-v0.1.md
mi-memoria-p4-flujos-productivos-subcharter-v0.1.md
mi-memoria-p5-interoperabilidad-controlada-subcharter-v0.1.md
```

Cada sub-charter debe ser tratado como entrada de planificación para Codex.

---

# 7. Restricciones Globales

## Permitido

- CLI local;
- Python local;
- Markdown;
- operaciones sobre workspace;
- preview;
- apply explícito;
- logs locales;
- validación;
- reportes `.md` y `.json`;
- LLM asistido bajo control del runtime.

## No permitido por defecto

- ejecución autónoma irreversible;
- modificaciones masivas sin plan;
- dependencias externas obligatorias;
- secretos;
- MCP funcional antes de P5;
- HTTPS antes de P5;
- APIs externas antes de P5;
- vector DB antes de madurez suficiente;
- persistencia indiscriminada de conversaciones.

---

# 8. Criterio de Madurez

Una fase se considera lista para cerrar cuando:

- sus comandos CLI existen;
- sus salidas son verificables;
- sus criterios de aceptación están cubiertos;
- sus restricciones están documentadas;
- no introduce deuda incompatible con el charter base;
- puede operar con ejemplos locales;
- distingue claramente preview, plan y apply.

---

# 9. Revisión de Consistencia

Este plan es consistente con la baseline porque:

- preserva el runtime separado del vault;
- mantiene la interoperabilidad al final;
- evita depender de APIs externas;
- conserva el LLM como asistente;
- prioriza verificabilidad;
- permite evolución incremental;
- mantiene `workspace/` como zona operacional;
- mantiene `$VAULT/00-40` como conocimiento real;
- reserva `$VAULT/context/` para metaconocimiento y gobernanza.
