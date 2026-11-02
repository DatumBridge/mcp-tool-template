# Agent entry — Weaver MCP tool

Read [`CONTRACT.md`](CONTRACT.md) before writing code. Do not start from a blank server file.

## Sequence

1. Read `CONTRACT.md`, `design.md`, and `contract/`.
2. Set `server_id` in `contract/tools.json`. Replace every `REPLACE_SERVER`.
3. Choose the language. Replace `Dockerfile` with an image that meets the image contract. Keep the six responsibilities in `design.md` even if the directories are idiomatic (`internal/`, `src/`, `cmd/`).
4. Implement transport, then one tool that calls a service and returns the error envelope.
5. Put the tool name in `contract/tools.json` and add `registry_docs/<tool_name>.md` in the same change. Copy [`registry_docs/_template.md`](registry_docs/_template.md). Set the `## Audience` row for that tool: `internal`, `external`, or `anonymous`, and `required` or `none`. Anonymous uses `none`.
6. Record only the `error_code` values the handler emits in `contract/error-codes.json`. Guides quote that file.
7. Run `sh scripts/check-contract.sh`, then the language tests named in `tests/README.md`.
8. Fill `docs/` from the behavior you implemented.
9. Run `sh scripts/check-contract.sh --publish`.
10. One git repository. Publish to the Weaver Tool Registry, deploy, then Setup — or host a public HTTPS origin and document `GET /register` for remote Sync (ADR-0174). See `README.md` and `CONTRACT.md` §7.

## Stop if

- The product needs a device WebSocket, pairing, or an edge catalog. That is a relay, not this template.
- A tool would approve, refuse, or authorize a business decision. Return data and leave the decision to Weaver.
- A required argument would be a token, API key, or `credentials_json` the model must invent.
