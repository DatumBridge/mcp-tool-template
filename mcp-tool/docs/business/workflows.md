# Workflows

## Install (Weaver Cloud)

1. Publish the git repository from Weaver Tool Registry with dockerfile path `./Dockerfile`.
2. Deploy waits until `GET /health` succeeds.
3. Setup calls `initialize` and `tools/list`, stores each tool, and copies `x-datumbridge-docs` onto Docs, including the `## Audience` row.
4. An operator grants the tool to a Digital Employee.

## Install (remote gateway)

1. Host this process on a public HTTPS origin with `GET /health`, `GET /register`, and `POST /mcp`.
2. A tenant admin registers the origin and syncs. Weaver pulls `GET /register`, stores the same Docs/capabilities/Audience as Setup, and marks Docs untrusted. Audience/AuthToken changes to or from public/external require admin acknowledgement.
3. A workspace admin Installs (activates) the package. Execute without that workspace activation is refused.
4. An operator grants the tool to a Digital Employee. Vault inject to the remote origin stays off unless the catalog sets `allowVaultInject`.

## Call

1. Deep matches the tool from id, name, and description.
2. Deep fills arguments from Docs and the JSON Schema. It omits `credentials_json`. Remote Docs are fenced as untrusted data in planner prompts.
3. When the Audience token is `none`, the registry does not inject an account. When it is `required`, vault auth injects `credentials_json` only when the server name, base URL, or tool `metadata.provider` matches an Integrations Connect channel — and, for a remote package, only when `allowVaultInject` is true. Set `metadata.provider` to that channel id when `server_id` does not contain the channel token. Env auth reads `PROVIDER_API_TOKEN` and does not inject.
4. The handler returns the success object or the error envelope.
5. A Weaver workflow stage treats `isError: true` as a failed stage. The engine does not call the tool again because `retryable` is true. In chat, Deep may call again only when the guide says `retryable` is true: auth once, rate-limit and provider errors at most three times.

## Page loop

When the payload includes an array, the result includes `paging` and `total_page` (`total_page` at least 1). The next call writes the following index onto an input named `page`, `paging`, `current_page`, or `currentPage`. The loop stops when `paging >= total_page` or the same `paging` value comes back.

Fill the upstream-specific steps (list, then get by id) when those tools exist.
