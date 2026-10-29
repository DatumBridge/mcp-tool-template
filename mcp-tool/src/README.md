# Source layout

These directories are the default map of the tool-server façade. Implement them in the language you chose, or point `design.md` at idiomatic paths with the same six responsibilities.

| Path | Responsibility |
|------|----------------|
| `transport/` | HTTP, session, JSON-RPC |
| `tools/` | Tool name, schema, validation, envelope |
| `services/` | Provider client |
| `errors/` | `error_code` values from `contract/error-codes.json` |
| `bind/` | Attach capabilities and `registry_docs` on `tools/list` |

The placeholder `Dockerfile` does not build a server. Replace it before publish.
