# System overview

`REPLACE_SERVER` is a Weaver tool-server. It implements MCP tools in-process and calls one upstream. Weaver Tool Registry installs it by building `Dockerfile`, then reading `tools/list` — or, off Weaver Cloud, by syncing `GET /register` from a public HTTPS origin (ADR-0174 / `mcp-tool-contract.md`).

```text
Studio / Deep → datumbridge-mcp (registry) → this process :8000   (Weaver Cloud)
                                              POST /mcp
                                              GET /health
                                              GET /register

Studio / Deep → datumbridge-mcp → https://provider.example     (remote gateway)
                                  GET /register (sync)
                                  POST /mcp (execute after workspace Install)
```

## What changed

| Change | Why | Components | Risk |
|--------|-----|------------|------|
| Each guide has one `## Audience` row. Setup or remote Sync copies it. | The server provider decides who can run the tool and whether a token is required. | `registry_docs/`, `scripts/check-contract.sh` | A guide without the row fails the contract check. |
| Remote gateway: public HTTPS `/register`, Docs `docsUntrusted`, workspace Install, vault inject opt-in. | Providers that skip DevSecOps still need the same Docs/Audience contract with Weaver-side SSRF and activation gates. | `GET /register`, CONTRACT §7 | Compromised origin can change Docs/schemas on sync; fence + ack reduce but do not remove that risk. |

## Dependencies

- Weaver gateway for credentials and the work-item workspace
- The upstream named in `design.md`
- Tool Registry Setup after each deploy that changes tools or guides — or remote Sync for an off-cloud origin

## Risks

A guide that drifts from the handler makes Deep send the wrong arguments. `scripts/check-contract.sh` and the language tests are the guard. A remote origin that changes Audience to public/external needs an admin ack on sync; remote Docs are fenced as untrusted in Deep/Design.
