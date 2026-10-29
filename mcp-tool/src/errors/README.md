# Errors

`contract/error-codes.json` is the only list of `error_code` values.

- Delete codes this server does not emit before you write guides.
- Guides and tests import this list. Do not add `invalid_argument` unless that string is in the file and a handler returns it.
- `retryable` in the JSON file is the value the handler sends.
