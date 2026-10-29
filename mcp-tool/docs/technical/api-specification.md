# API

Two HTTP routes.

## `GET /health`

- Auth: none
- Response: `200` `{"status":"ok"}`

## `POST /mcp`

Streamable HTTP JSON-RPC 2.0. Protocol `2024-11-05`.

`initialize`, `tools/list`, `tools/call`, and JSON-RPC errors are HTTP 200. Any other status stops Setup before the registry reads the body.

| Method | Success | Failure |
|--------|---------|---------|
| `initialize` | `200`, header `Mcp-Session-Id`, `result.protocolVersion`, `result.capabilities.tools`, `result.serverInfo` | `-32600` bad request, `-32700` parse |
| `tools/list` | `result.tools[]` | `-32000` if the session header is missing or unknown |
| `tools/call` | `result.content[].text` JSON envelope, `isError` | `-32000` missing session, `-32602` bad arguments, `-32601` unknown tool, envelope with `isError: true` for handler failures |

`text` validates against `contract/envelope.schema.json`.

Tool names, arguments, samples, and the `## Audience` row live in `registry_docs/`. The schema annotations are in `CONTRACT.md` section 4. Setup copies that row. This server does not expose an admin route that changes it.

This server has no REST admin API. Do not return the tool envelope from a route other than `/mcp`.
