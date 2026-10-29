# Transport

Own `GET /health` and `POST /mcp`.

- Create an opaque session id on `initialize` and set `Mcp-Session-Id`.
- Gate `tools/list` and `tools/call` on that id. Missing or unknown → JSON-RPC `-32000`, message `invalid or missing Mcp-Session-Id (call initialize first)`.
- Dispatch methods. Unknown method or unknown tool → `-32601`.
- Schema failures → `-32602` before the tool handler runs.
- Return `Content-Type: application/json`.
- Do not log the request body when it may contain upstream text or credentials.
- Do not call the provider from this layer.
