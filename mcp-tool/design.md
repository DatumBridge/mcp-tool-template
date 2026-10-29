# Design

Class: **tool-server**. This process implements tools. It does not relay to a device.

Pattern: tool-server façade in [`CONTRACT.md`](CONTRACT.md) section 2.

## Server

| Field | Value |
|-------|--------|
| `server_id` | `REPLACE_SERVER` |
| Upstream | Fill: which system this server calls |
| Auth | Fill one: `vault` or `env`. Vault: optional `credentials_json` on each tool, and set the registry tool `metadata.provider` to the Integrations channel id when `server_id` does not contain that channel token. Env: `PROVIDER_API_TOKEN` only. Not both. |

## Layer map

Change the path column if the language uses other directories. Do not drop a row.

| Responsibility | Path |
|----------------|------|
| Entrypoint | Fill |
| Transport | `src/transport/` |
| Tools | `src/tools/` |
| Services | `src/services/` |
| Errors | `src/errors/` |
| Bind | `src/bind/` |

## Decisions

- Protocol version stays `2024-11-05` until Weaver's registry client changes.
- Listen port stays 8000.
- Business decisions stay in Weaver. This server returns data.
- Each tool's `## Audience` row is this server's decision: who can run it, and whether it needs a token. Anonymous uses `none`.
- No database unless the upstream integration cannot be stateless. Sessions may live in memory with a TTL.

## Non-goals

- Device WebSocket, pairing, edge catalog
- Tools named approve, authorize, or refuse
- A second provider in this repository

## Rollback

Redeploy the previous image. Deactivate the registry rows for tools this version added.
