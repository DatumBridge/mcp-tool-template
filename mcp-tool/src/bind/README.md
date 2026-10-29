# Registry bind

On each tool in `tools/list`:

1. Set input schema `x-datumbridge-capabilities` to `["<server_id>.<tool_name>"]`.
2. Read `registry_docs/<tool_name>.md`. Strip ends. If length is greater than 24 000 characters, fail startup. Do not truncate.
3. Set `x-datumbridge-docs` to that markdown. The file includes one `## Audience` row. Do not invent that row here; copy the guide.

The image must contain `registry_docs/`. Setup copies the markdown onto the tool Docs field and deletes the schema key.
