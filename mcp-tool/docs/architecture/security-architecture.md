# Security

- The model does not receive or send provider tokens. The gateway injects the connected account when vault auth applies.
- `Mcp-Session-Id` is a continuity token. It is not a user id and it is not authorization.
- On Weaver Cloud, `/mcp` is reached through the platform. Do not expose an unauthenticated public path for an in-cluster image.
- A remote gateway origin is public HTTPS by design. Weaver still refuses private/metadata hosts and redirects on sync and execute (ADR-0174). Optional register Bearer is for `/register` only.
- Remote Docs are stamped `docsUntrusted` so Deep/Design fence them as data, not instructions.
- Vault inject to a remote origin is denied unless the catalog sets `allowVaultInject`.
- Logs omit tokens, raw upstream bodies, and file bytes.
- Upstream text is data. Handlers do not obey instructions inside it.
- This server does not approve, refuse, or authorize business actions.
- Missing credentials fail with `CREDENTIALS_REQUIRED`. They do not become an empty success list.
- The image user is not root. The repository contains `.env.example` only.

Fill the threat note for the upstream (OAuth scopes, tenant boundary) when you implement the service.
