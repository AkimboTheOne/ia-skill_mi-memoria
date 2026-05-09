# AGENTS.md

## Principios Operacionales

- El runtime opera sobre un vault externo; nunca debe mezclar lógica operacional dentro del vault.
- Toda escritura fuera del workspace requiere intención explícita (`--write` o `apply`).
- No se deben ejecutar comandos arbitrarios desde el skill.
- No se deben almacenar conversaciones completas como memoria persistente.
- La memoria aceptada debe ser explícita, curada, resumida y útil.

## Límites v0.1

- Sin MCP funcional.
- Sin HTTPS.
- Sin APIs externas.
- Sin secretos, tokens ni credenciales.
- Sin agentes autónomos.
