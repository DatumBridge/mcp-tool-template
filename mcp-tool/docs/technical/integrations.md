# Integrations

| System | Direction | Contract |
|--------|-----------|----------|
| Weaver Tool Registry | Inbound | `POST /mcp` after deploy. Port 8000. |
| Upstream | Outbound | Fill the base URL, auth style, and status mapping. |

Status mapping:

| Upstream | `error_code` | retryable |
|----------|--------------|-----------|
| No credential | `CREDENTIALS_REQUIRED` | false |
| 401 | `AUTH_ERROR` | true |
| 403 | `PERMISSION_DENIED` | false |
| 429 | `RATE_LIMIT` | true |
| 5xx / timeout | `PROVIDER_ERROR` | true |
| Unmapped | `UNKNOWN_ERROR` | false |

A tool that looks up an id adds `NOT_FOUND` (`retryable: false`) to `contract/error-codes.json` and to that tool's guide. Remove a row the handler does not emit, and delete that code from the JSON file.
