# API

Three HTTP routes.

## `GET /health`

- Auth: none
- Response: `200` `{"status":"ok"}`

## `GET /register`

- Auth: none (Weaver may send an optional Bearer token the tenant admin stored for this origin)
- Session: none. Do not require `Mcp-Session-Id`.
- Response: `200` `application/json` with `server_id`, `name`, `version`, and `tools[]`.
- Each tool matches `tools/list`: `name`, `description`, `inputSchema` (with `x-datumbridge-capabilities` and `x-datumbridge-docs`), optional `outputSchema`.
- Weaver pulls this route when a tenant admin registers a remote MCP server that is not deployed on Weaver Cloud (ADR-0174 / `mcp-tool-contract.md`). Sync stores Docs, capabilities, and Audience the same way Setup stores `tools/list`, stamps remote Docs `docsUntrusted`, and does **not** grant execute rights. A workspace admin must Install (activate) the package before Role Agents or Test Tool can call `POST /mcp` on this origin.
- Weaver accepts only a public HTTPS `baseUrl`. Loopback, private, link-local, CGNAT, and cloud-metadata hosts are refused on register, sync, and execute. Redirects are refused.

## `POST /mcp`

Streamable HTTP JSON-RPC 2.0. Protocol `2024-11-05`.

`initialize`, `tools/list`, `tools/call`, and JSON-RPC errors are HTTP 200. Any other status stops Setup before the registry reads the body.

| Method | Success | Failure |
|--------|---------|---------|
| `initialize` | `200`, header `Mcp-Session-Id`, `result.protocolVersion`, `result.capabilities.tools`, `result.serverInfo` | `-32600` bad request, `-32700` parse |
| `tools/list` | `result.tools[]` | `-32000` if the session header is missing or unknown |
| `tools/call` | `result.content[].text` JSON envelope, `isError` | `-32000` missing session, `-32602` bad arguments, `-32601` unknown tool, envelope with `isError: true` for handler failures |

`text` validates against `contract/envelope.schema.json`.

Tool names, arguments, samples, and the `## Audience` row live in `registry_docs/`. The schema annotations are in `CONTRACT.md` section 4. Setup or remote Sync copies that row. This server does not expose an admin route that changes it.

`/register` is a read-only install card. Do not return the tool call envelope from it. This server has no other REST admin API.
