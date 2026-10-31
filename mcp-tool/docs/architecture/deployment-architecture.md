# Deployment

Weaver deploy builds `./Dockerfile` and runs the container on port **8000** in the MCP tools namespace. The registry base URL uses that port.

| Probe | Path |
|-------|------|
| Process health | `GET /health` |
| Remote install card | `GET /register` |
| Tool install on Weaver Cloud | `POST /mcp` `initialize`, then `tools/list` |

A provider that keeps the process off Weaver Cloud still exposes `/register` and `/mcp`. Weaver syncs the card and calls the provider origin on execute.

The image runs as a non-root user. Secrets arrive as environment variables from the platform, not from the image.

## Rollback

Deploy the previous image. Deactivate registry tools that only the new image exposes. Guides update on the next Setup.

Fill the repository URL and Kubernetes name when you publish.
