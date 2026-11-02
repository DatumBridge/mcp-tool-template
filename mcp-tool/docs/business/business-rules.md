# Business rules

## BR-1 — Tools return data

This server does not approve, refuse, or authorize. Weaver workflows and a person keep those decisions.

## BR-2 — Guides match handlers

Each tool in `contract/tools.json` has `registry_docs/<tool_name>.md`. Samples, error codes, and cases match the handler. Codes live in `contract/error-codes.json`.

## BR-3 — Credentials stay off the model call

Deep omits tokens. Vault OAuth still declares optional `credentials_json` so the registry can inject the connected account. A deployment-token server reads `PROVIDER_API_TOKEN` and does not declare that property. A missing account is `CREDENTIALS_REQUIRED` and is not retried.

## BR-4 — Identifiers come from a prior result or the user

The server does not accept `"example-id"` as a real id. Not-found is `NOT_FOUND`.

## BR-5 — The server declares who can run each tool

`registry_docs/<tool_name>.md` has one `## Audience` row. `Who` is `internal` (staff), `external` (authenticated caller), or `anonymous`. `Token` is `required` or `none`. Anonymous uses `none`. Setup or remote sync (`GET /register`, ADR-0174) copies the row. An admin does not change it. A remote sync that would change Audience or AuthToken to or from public/external requires tenant-admin acknowledgement in Weaver. Anonymous still runs only through a Digital Employee and does not receive a connected account.

## BR-6 — Lists expose pages

A success payload that contains an array includes numeric `paging` (first page is 1) and `total_page`.

## BR-7 — Remote origin is public HTTPS and workspace-scoped

A provider that skips Weaver Cloud deploy hosts this process on a public HTTPS origin. Weaver refuses private and metadata hosts on sync and execute. Remote Docs are stamped untrusted for planner fences. The package starts inactive; a workspace admin must Install before execute. Vault credentials are not sent to that origin unless `allowVaultInject` is set.

Add a rule here when a tool gains a business constraint. Delete a rule when the handler no longer enforces it.
