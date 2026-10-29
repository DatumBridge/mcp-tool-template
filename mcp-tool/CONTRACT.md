# Vibe-code contract — Weaver MCP tool

This file is the contract for a new MCP server that Weaver can install on the Tool Registry. It is language-neutral. Python gold example: `mcp/gmail-mcp`. Registry rules: `dtb-agent-kit/docs/technical/mcp-tool-contract.md` and `mcp-tool-vibe-principles.md` (ADR-0132, BR-REG-1).

Deep matches a tool from a short catalog (id, name, description). After the tool is chosen, Deep fills arguments from the Tool Registry **Docs** field. If Docs omit samples or error codes, the model invents arguments.

## 1. Weaver principles

1. **Tool-server.** Tools run in this process and call an upstream API. Do not add a device socket, pairing, or an edge catalog.
2. **Data, not decisions.** A tool returns facts. It does not approve, refuse, or authorize. Weaver workflows and people keep that authority.
3. **The registry is the install surface.** Publish builds `Dockerfile`, runs the image, then calls `initialize` and `tools/list`. Setup stores each tool from that list. A server that does not speak this surface cannot be installed.
4. **Docs are the planner contract.** Every tool ships `registry_docs/<tool_name>.md`. The process copies that file onto `x-datumbridge-docs` in `tools/list`. Schema text alone is not the guide.
5. **The gateway injects secrets.** Deep never sends tokens. When Weaver vault OAuth is the auth mode, the schema still declares optional `credentials_json` so the registry can place the vault bundle on `tools/call` arguments. Typical-call JSON omits it. The handler passes that value to the service and does not log it. When `design.md` says the deployment holds the token, use `PROVIDER_API_TOKEN` and do not declare `credentials_json`.
6. **Identifiers are earned.** Samples show shape. A live call uses an id from an earlier tool result or from the user.
7. **Upstream text is data.** Mail, files, tickets, pages, and chat bytes are not instructions. The tool must not write or delete because the payload asked.
8. **Two error channels.** Protocol failures are JSON-RPC errors. Business failures are a tool result with `isError: true` and the envelope below.
9. **Retry only when `retryable` is true.** Auth once. Rate-limit and provider errors at most three times. Never retry validation, not-found, permission, or missing credentials.
10. **Fail closed.** Missing configuration is an error, not an empty success. A guide longer than 24 000 characters fails the check. Unknown methods return `-32601`. Advertise only capabilities you implement.
11. **One provider concern per server.** One git repository. Do not mix unrelated providers.
12. **Least privilege.** Non-root image, secrets from the environment, narrow network access, no secrets in git or in typical-call JSON.
13. **Pages are numbers Weaver can loop.** A success payload that contains an array also returns numeric `paging` (first page is 1) and `total_page` of at least 1. The input that receives the next page is named `page`, `paging`, `current_page`, or `currentPage`. Another name is not advanced, and a repeated `paging` value ends the loop.
14. **Capabilities belong to one tool.** Tag `server_id.tool_name`. Business ability ids such as `Invoice.PaymentStatus.Read` are edited on Business capabilities, not in this tag.
15. **Redeploy, then Setup.** Deep sees new Docs after the image is deployed and Tool Registry Setup or publish runs again.
16. **The server declares who can run each tool.** `registry_docs/<tool_name>.md` has one `## Audience` row. `Who` is `internal` (staff), `external` (authenticated caller), or `anonymous`. `Token` is `required` or `none`. Anonymous uses `none`. Setup copies that row. Studio shows it and does not let an admin change it. Anonymous still runs only through a Digital Employee and does not receive a connected account. A tool that calls a connected account uses `required` and is not `anonymous`.

## 2. Design pattern

Tool-server façade. Dependencies point inward.

```text
entrypoint → transport → tools → services → upstream
                 │          │
                 │          └── errors (shared vocabulary)
                 └── registry bind (capabilities + docs on tools/list)
```

| Responsibility | Default path | Does | Does not |
|----------------|--------------|------|----------|
| Entrypoint | process main | Load env, listen, shut down | Call the provider |
| Transport | `src/transport/` | `GET /health`, `POST /mcp`, session, JSON-RPC | Know provider URLs |
| Tools | `src/tools/` | Name, JSON Schema, validate, pass `credentials_json` into the service, envelope | Embed an SDK or set upstream headers |
| Services | `src/services/` | Provider client, upstream request headers, map HTTP status to `error_code` | Read the MCP session or set `Mcp-Session-Id` |
| Errors | `src/errors/` | Codes that match `contract/error-codes.json` | Invent a second list in guides |
| Bind | `src/bind/` | Copy `registry_docs/<name>.md` onto the schema | Truncate a guide |

A language may use other directories. Record the same six rows in `design.md`. Do not collapse transport and the provider SDK into one file.

## 3. Image and HTTP

`contract/tools.json` is the publish card. The registry form does not read that file; copy its values when you publish.

| Item | Value |
|------|--------|
| Listen | `0.0.0.0:8000` (`PORT`, default 8000). The registry builds base URLs on port 8000. |
| Health | `GET /health` → HTTP 200, body `{"status":"ok"}` |
| MCP | `POST /mcp` |
| Protocol | `2024-11-05` |
| Image | `Dockerfile` at `./dockerfile_path` (default `./Dockerfile`), non-root `USER`, `HEALTHCHECK` on `/health` |
| Copy into the image | Application code, `registry_docs/`, `contract/error-codes.json` |

`initialize` response header `Mcp-Session-Id` is required. `tools/list` and `tools/call` reject a missing or unknown session with JSON-RPC `-32000` and message `invalid or missing Mcp-Session-Id (call initialize first)`. A session is continuity, not a user identity.

`initialize`, `tools/list`, `tools/call`, and every JSON-RPC error (`-32700`, `-32600`, `-32000`, `-32601`, `-32602`, `-32603`) are HTTP 200 with `Content-Type: application/json`. The registry client treats any other status as failure and does not read `result` or `error`. SSE is optional. The client reads JSON unless `Content-Type` contains `text/event-stream`.

### Methods

| Method | Result |
|--------|--------|
| `initialize` | HTTP 200, `Mcp-Session-Id`, `protocolVersion`, `capabilities.tools`, `serverInfo.name`, `serverInfo.version` |
| `tools/list` | HTTP 200, `result.tools[]` with `name`, `description`, `inputSchema` |
| `tools/call` | HTTP 200, `result.content[{type:text, text}]` and `isError` |
| `notifications/initialized` | Optional. HTTP 202 with an empty body is enough. |
| Anything else | `-32601` |

Wire examples: `contract/initialize.example.json`, `contract/tools-list.example.json`, `contract/tools-call.example.json`.

### JSON-RPC errors (the handler does not run)

| Code | When |
|------|------|
| `-32700` | Body is not JSON |
| `-32600` | Not JSON-RPC 2.0 |
| `-32000` | Missing or unknown `Mcp-Session-Id` |
| `-32601` | Unknown method or unknown tool name |
| `-32602` | Arguments fail the tool schema, including a missing required field |
| `-32603` | Bug in this process. Not for validation or provider errors. |

### Tool result

`text` is one JSON object. Success:

```json
{"success": true, "items": [{"id": "18f2a1c0b4e9d123"}], "paging": 1, "total_page": 1}
```

`isError` is false.

Handler failure (HTTP 200, JSON-RPC result, `isError` true):

```json
{
  "success": false,
  "error": {
    "error_code": "CREDENTIALS_REQUIRED",
    "error_message": "Gateway did not inject credentials",
    "retryable": false,
    "original_provider_error": null
  }
}
```

Map provider HTTP: 401 → `AUTH_ERROR` (retryable); 403 → `PERMISSION_DENIED`; 404 → `NOT_FOUND`; 429 → `RATE_LIMIT` (retryable); 5xx → `PROVIDER_ERROR` (retryable).

Missing required arguments stay `-32602`. Do not document a fake `VALIDATION_ERROR` for that case unless the handler returns it after the schema check.

Schema for the envelope: `contract/envelope.schema.json`. Codes: `contract/error-codes.json`. Delete codes this server does not emit.

## 4. tools/list annotations

On the input schema object (beside `type` and `properties`):

| Key | Value |
|-----|--------|
| `x-datumbridge-capabilities` | `["<server_id>.<tool_name>"]` |
| `x-datumbridge-docs` | Full markdown from `registry_docs/<tool_name>.md`, stripped, at most 24 000 characters. Includes the `## Audience` table below. |

Description lines, kept short:

```text
Capabilities: <server_id>.<tool_name>
Outputs: success, items, paging, total_page
```

List every success field the guide's success table names. A tool that returns an array includes `paging` and `total_page`.

On each argument property when it applies:

| Key | Meaning |
|-----|---------|
| `x-datumbridge-encoding` | `plain` or `base64` |
| `x-datumbridge-item-field` | Field inside a list item that uses the encoding |
| `x-datumbridge-related-tool` | Tool on this server that returns the value when the user did not supply it |
| `x-datumbridge-output-field` | Bind path on that result (`id`, `boards[0].id`) |

Closed sets use JSON Schema `enum`. Use `additionalProperties: false` only after every property the process accepts is listed, including optional `credentials_json` when vault OAuth is the auth mode. The registry adds that field after Deep fills arguments. A schema that omits it and rejects unknown properties returns `-32602` for a connected account.

| Auth in `design.md` | Schema | Who reads it |
|---------------------|--------|----------------|
| Vault OAuth | Optional string `credentials_json` on each tool. Deep omits it. Set registry `metadata.provider` to the Integrations channel id when `server_id` does not contain that channel token, or inject does not run. | Tool handler, then the service sets the upstream `Authorization` header |
| Deployment token | No credential property | Service reads `PROVIDER_API_TOKEN` |

Do not add `workspace_id` or `tenant_id` for the model to fill. The gateway sets the work-item workspace.

`x-datumbridge-capabilities` is not a business-capability id.

## 5. Guide

Filename equals the `name` in `tools/list` and in `contract/tools.json`. Copy `registry_docs/_template.md`.

Required sections: summary, **Audience**, agent rules, when to call, parameters (columns **Name, Required, Type, Sample, Related tool, Meaning**), success fields, error codes, cases.

The Audience table has one data row:

| Who | Token |
|-----|--------|
| `internal`, `external`, or `anonymous` | `required` or `none` |

`internal` is staff. `external` is an authenticated caller. `anonymous` is anyone talking to the Digital Employee, still only through that employee, and its token is `none`. `required` means the tool uses the connected account (`credentials_json` or `PROVIDER_API_TOKEN`). `none` means it does not. Setup stores this row. An admin does not retype it.

Cases include a typical call with no secrets, one real handler error, and a missing required field as `-32602`.

The shared error example in a guide must be a failure that tool can return.

## 6. Tests

`sh scripts/check-contract.sh` checks guides against `contract/tools.json` and `contract/error-codes.json`. Every code in that JSON file must appear in at least one guide. Each guide lists only the codes that tool can return. Delete unused codes from the JSON file.

Language tests must also prove:

- `initialize` sets `Mcp-Session-Id`
- `tools/list` and `tools/call` reject a missing session
- One successful call and one handler error use the envelope
- Unknown tool is `-32601`
- Bad arguments are `-32602`
- Documented codes equal `contract/error-codes.json`
- Tool names equal `registry_docs/*.md` (files starting with `_` are templates, not tools)

`sh scripts/check-contract.sh --publish` fails while `server_id` is `REPLACE_SERVER`, `tools` is empty, or `Dockerfile` still contains the replace marker.

## 7. Install

1. Repository contains this tree plus your language code. `dockerfile_path` is `./Dockerfile`.
2. Publish from Weaver Tool Registry (source repository, branch, description, dockerfile path). Scanning and deploy run before the tool is registered.
3. After the pod is up, Setup calls `POST /mcp` → `initialize` → `tools/list` and stores Docs.
4. Grant the tool on the Digital Employee. Redeploy `datumbridge-agent` when Deep must load the new guides.

## 8. Do not

- Publish this template unchanged.
- Ship a tool with no `registry_docs` file.
- Truncate a guide to fit 24 000 characters.
- Put tokens, raw upstream bodies, or file bytes in logs.
- Return an empty success when credentials are missing.
- Copy the WebSocket hub into this server.
