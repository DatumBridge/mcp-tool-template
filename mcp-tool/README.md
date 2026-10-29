# MCP tool template

Copy this folder to a new git repository and vibe-code the server in any language. The copy is what you publish to the Weaver Tool Registry. This folder is not a server.

```bash
cp -R mcp/templates/mcp-tool ../my-service-mcp
cd ../my-service-mcp
# remove the template git metadata if you copied from a repo that has one
```

Agents start at [`AGENTS.md`](AGENTS.md). Humans and agents follow [`CONTRACT.md`](CONTRACT.md).

## What you replace

| File | Replace with |
|------|----------------|
| `contract/tools.json` `server_id` | Stable id, lowercase snake_case, used in `Capabilities:` |
| `contract/tools.json` `tools` | Array of tool names, for example `["list_items"]` |
| `Dockerfile` | Your language image. Keep port 8000, `/health`, non-root, `HEALTHCHECK`. |
| `src/` | Implementation, or your language's directories mapped in `design.md` |
| `registry_docs/_template.md` | One `registry_docs/<tool_name>.md` per tool |
| `docs/` | The behavior you shipped |

## Install check

```bash
sh scripts/check-contract.sh
sh scripts/check-contract.sh --publish
```

`--publish` is the gate before Tool Registry publish. It fails while the server id is still `REPLACE_SERVER`, no tools are declared, or the Dockerfile is still the placeholder.

## Publish

1. Push the repository.
2. In Weaver Tool Registry, publish that repository. Set dockerfile path to `./Dockerfile`. The description matches `contract/tools.json` `description`.
3. When the deployment is healthy, run Setup so `tools/list` is stored, including Docs.
4. Grant tools on the Digital Employee.

The registry calls `POST /mcp` on port **8000**, protocol **2024-11-05**, and requires response header `Mcp-Session-Id`.

Filled Python example: `mcp/gmail-mcp`.
