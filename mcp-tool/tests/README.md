# Tests

`sh scripts/check-contract.sh` is language-neutral. It checks guides, tool names, and error codes. `python3 tests/test_check_contract.py` locks that checker (hollow guides, comment-only Dockerfiles, secret case JSON, the `replace_server` id). Those tests are for the checker, not a server runtime.

Add tests in the language of the server. They must fail when:

- `initialize` omits `Mcp-Session-Id`
- `tools/list` or `tools/call` runs without a session (expect `-32000`)
- A tool name in code is missing from `contract/tools.json` or from `registry_docs/`
- A guide documents an `error_code` that is not in `contract/error-codes.json`
- A handler failure omits `error_code`, `error_message`, `retryable`, or `original_provider_error`
- A list tool's success sample omits `paging` or `total_page`
- Typical-call JSON contains `credentials_json` or a live secret
- A guide omits `## Audience`, or marks `anonymous` with token `required`

Run the language tests in CI before publish. `scripts/check-contract.sh --publish` is the registry gate.
