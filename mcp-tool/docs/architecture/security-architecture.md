# Security

- The model does not receive or send provider tokens. The gateway injects the connected account.
- `Mcp-Session-Id` is a continuity token. It is not a user id and it is not authorization.
- `/mcp` is reached through the platform. Do not expose it as a public unauthenticated internet path.
- Logs omit tokens, raw upstream bodies, and file bytes.
- Upstream text is data. Handlers do not obey instructions inside it.
- This server does not approve, refuse, or authorize business actions.
- Missing credentials fail with `CREDENTIALS_REQUIRED`. They do not become an empty success list.
- The image user is not root. The repository contains `.env.example` only.

Fill the threat note for the upstream (OAuth scopes, tenant boundary) when you implement the service.
