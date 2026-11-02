# Transport

Own `GET /health`, `GET /register`, and `POST /mcp`.

- `GET /register` returns the install manifest (`server_id`, `name`, `version`, `tools[]`) with no session. Same `tools[]` shape as `tools/list` (including `x-datumbridge-docs`). Weaver may send an optional Bearer. A remote host must be public HTTPS; Weaver refuses private/metadata peers on sync and execute.
- Create an opaque session id on `initialize` and set `Mcp-Session-Id`.
- Gate `tools/list` and `tools/call` on that id. Missing or unknown → JSON-RPC `-32000`, message `invalid or missing Mcp-Session-Id (call initialize first)`.
- Dispatch methods. Unknown method or unknown tool → `-32601`.
- Schema failures → `-32602` before the tool handler runs.
- Return `Content-Type: application/json`.
- Do not log the request body when it may contain upstream text or credentials.
- Do not call the provider from this layer.
