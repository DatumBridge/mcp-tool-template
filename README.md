# MCP templates

The copy-and-fill template is at `mcp/templates/mcp-tool`. Copy that folder into its own git repository, implement the server in whatever language you want, and publish that repository to the Weaver Tool Registry.

```bash
cp -R mcp/templates/mcp-tool ../my-service-mcp
cd ../my-service-mcp
```

Start with `AGENTS.md` and `CONTRACT.md`. The folder is not a server yet. `sh scripts/check-contract.sh --publish` fails until you set a real `server_id`, declare tools, and replace the placeholder `Dockerfile`.

The layout is a tool-server façade: transport, tools, services, errors, and registry bind. Dependencies point inward. A language can use its own directories if `design.md` keeps those six rows.

What Weaver installs:

- The image listens on port **8000**, with `GET /health` and `POST /mcp` (protocol `2024-11-05`, header `Mcp-Session-Id`).
- Each tool has `registry_docs/<tool_name>.md`. The `## Audience` row says who can run it (`internal`, `external`, or `anonymous`) and whether it needs a token (`required` or `none`). Setup copies that guide, including the row. Anonymous uses `none`.
- Vault OAuth declares optional `credentials_json` so the registry can inject the connected account. Deep does not send it. If the server id does not match an Integrations channel, set `metadata.provider`. A deployment token uses `PROVIDER_API_TOKEN` instead.
- List results return numeric `paging` and `total_page`. The next page is written to an input named `page`, `paging`, `current_page`, or `currentPage`.
- A workflow stage fails when the tool returns `isError`. It does not call again on its own.

| Folder | Use |
|--------|-----|
| [`mcp-tool/`](mcp-tool/README.md) | New MCP server in any language. Installs on the Weaver Tool Registry. |

Python servers that already follow `gmail-mcp` stay the filled example. This folder is the starting tree when the language is not chosen yet, or is not Python.
