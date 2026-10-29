# Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `PORT` | no | `8000` | Listen port. Do not change the published port. |
| `LOG_LEVEL` | no | `info` | Log verbosity. Never log secrets or raw upstream bodies. |
| `PROVIDER_API_TOKEN` | when the gateway does not inject a credential | empty | Upstream token. Set by the platform secret, not by the model. |

See `.env.example`. Add a row when you add a variable. Do not add a variable for a feature you have not implemented.

`contract/tools.json` is the publish card a person copies onto the Tool Registry form. The running process may read `server_id` from it. The registry does not fetch this file.
