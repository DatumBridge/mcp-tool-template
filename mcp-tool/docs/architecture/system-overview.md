# System overview

`REPLACE_SERVER` is a Weaver tool-server. It implements MCP tools in-process and calls one upstream. Weaver Tool Registry installs it by building `Dockerfile`, then reading `tools/list`.

```text
Studio / Deep → datumbridge-mcp (registry) → this process :8000
                                              POST /mcp
                                              GET /health
```

## What changed

| Change | Why | Components | Risk |
|--------|-----|------------|------|
| Each guide has one `## Audience` row. Setup copies it. | The server provider decides who can run the tool and whether a token is required. | `registry_docs/`, `scripts/check-contract.sh` | A guide without the row fails the contract check. |

## Dependencies

- Weaver gateway for credentials and the work-item workspace
- The upstream named in `design.md`
- Tool Registry Setup after each deploy that changes tools or guides

## Risks

A guide that drifts from the handler makes Deep send the wrong arguments. `scripts/check-contract.sh` and the language tests are the guard.
