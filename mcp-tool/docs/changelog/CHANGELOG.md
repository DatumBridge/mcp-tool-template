# Changelog

## 2026-11-02

### Changed

- **Remote gateway contract aligned with `mcp-tool-contract.md` / ADR-0174.** Off Weaver Cloud: public HTTPS origin, `GET /register` carries the same Docs/capabilities/Audience as `tools/list`, Weaver stamps remote Docs untrusted, workspace Install before execute, vault inject opt-in (`allowVaultInject`), and Audience/AuthToken changes to or from public/external need tenant-admin acknowledgement on sync. See `CONTRACT.md` §7, BR-7, and `docs/technical/api-specification.md`.

## 2026-10-29

### Changed

- Each tool guide must include one `## Audience` row: who can run the tool (`internal`, `external`, or `anonymous`) and whether it needs a token (`required` or `none`). Anonymous uses `none`. `scripts/check-contract.sh` rejects a missing row and rejects anonymous with a required token. See `CONTRACT.md` principle 16.

## 2026-10-26

### Added

- Language-neutral Weaver MCP tool template: façade layout, vibe-code contract, registry guides, and `scripts/check-contract.sh`.

### Changed

### Fixed

### Removed
