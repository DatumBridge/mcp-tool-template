# Changelog

## 2026-10-29

### Changed

- Each tool guide must include one `## Audience` row: who can run the tool (`internal`, `external`, or `anonymous`) and whether it needs a token (`required` or `none`). Anonymous uses `none`. `scripts/check-contract.sh` rejects a missing row and rejects anonymous with a required token. See `CONTRACT.md` principle 16.

## 2026-10-26

### Added

- Language-neutral Weaver MCP tool template: façade layout, vibe-code contract, registry guides, and `scripts/check-contract.sh`.

### Changed

### Fixed

### Removed
