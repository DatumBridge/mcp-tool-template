# Components

```text
entrypoint
  → transport (session, JSON-RPC)
    → tools (schema, envelope)
      → services (upstream)
    → bind (registry_docs → x-datumbridge-docs)
errors ← tools, services
```

| Piece | Role |
|-------|------|
| Transport | `/health`, `/mcp`, `Mcp-Session-Id` |
| Tools | Stable names and JSON Schema |
| Services | Upstream HTTP and status mapping |
| Bind | Planner Docs |
| Errors | `contract/error-codes.json` |

Fill the concrete type names when you implement them.
