# Tools

One tool, one stable `snake_case` name.

- `tools/list` and `tools/call` use the same name and the same JSON Schema.
- Description includes `Capabilities: <server_id>.<tool_name>` and `Outputs:` listing real success fields.
- Validate arguments, call the service, return the envelope in `contract/envelope.schema.json`.
- `isError` is true only when `success` is false.
- An array result includes numeric `paging` and `total_page`.
- Vault OAuth: declare optional `credentials_json`. Deep omits it. The registry injects it. Pass that string into the service. Do not log it.
- Deployment token: do not declare `credentials_json`. The service reads `PROVIDER_API_TOKEN`.
- Record which mode `design.md` uses. Do not implement both on one tool.
- The guide's `## Audience` token matches that mode: `required` when the tool uses the account, `none` when it does not. `anonymous` uses `none`.
