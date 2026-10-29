#!/usr/bin/env python3
"""Language-neutral registry contract check for a Weaver MCP tool server.

The checker is not the server. Implement the server in any language.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_GUIDE = 24000
DOCKER_MARKER = "Replace this Dockerfile with your language image before publish"
NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
CODE_ROW = re.compile(
    r"^\|\s*`([A-Z][A-Z0-9_]*)`\s*\|\s*(true|false)\s*\|",
    re.M | re.I,
)
FENCE = re.compile(r"```json\s*(.*?)```", re.S)
SECRET_KEY = re.compile(
    r'"(credentials_json|credentials_path|api_key|access_token|password|secret|token|authorization)"\s*:',
)
EXAMPLE_ID = "example-id"


def fail(messages: list[str]) -> None:
    for message in messages:
        print(f"contract: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail([f"{path.relative_to(ROOT)}: {exc}"])
    return {}


def parameter_rows(text: str) -> list[str]:
    part = text.split("## Parameters", 1)[-1].split("## ", 1)[0]
    rows = []
    for line in part.splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+", line):
            continue
        if "Sample" in line and "Name" in line:
            continue
        rows.append(line)
    return rows


def audience_errors(name: str, text: str) -> list[str]:
    if "## Audience" not in text:
        return []
    part = text.split("## Audience", 1)[-1].split("\n## ", 1)[0]
    row: list[str] | None = None
    for line in part.splitlines():
        if not line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+", line):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        cells = [cell for cell in cells if cell]
        if len(cells) < 2 or cells[0].lower() == "who":
            continue
        row = cells
        break
    if row is None:
        return [f"{name}: ## Audience needs one Who / Token row"]
    who, token = row[0].lower(), row[1].lower()
    errors: list[str] = []
    if who not in {"internal", "external", "anonymous"}:
        errors.append(f"{name}: Audience Who must be internal, external, or anonymous")
    if token not in {"required", "none"}:
        errors.append(f"{name}: Audience Token must be required or none")
    if who == "anonymous" and token == "required":
        errors.append(f"{name}: anonymous cannot require an authentication token")
    return errors


def case_blocks(text: str) -> str:
    return text.split("## Cases", 1)[-1] if "## Cases" in text else ""


def guide_errors(name: str, text: str, codes: dict[str, bool]) -> list[str]:
    errors: list[str] = []
    if not text.startswith(f"# {name}\n") and not text.startswith(f"# {name}\r\n"):
        errors.append(f"{name}: first line must be '# {name}'")
    for section in (
        "## Audience",
        "## Agent rules",
        "## When to call",
        "## Parameters",
        "## Success fields",
        "## Error codes",
        "## Cases",
    ):
        if section not in text:
            errors.append(f"{name}: missing {section}")
    header = "| Name | Required | Type | Sample | Related tool | Meaning |"
    if header not in text:
        errors.append(f"{name}: parameter table is missing the Sample and Related tool columns")
    if not parameter_rows(text):
        errors.append(f"{name}: parameter table has no rows")
    if "untrusted" not in text.lower():
        errors.append(f"{name}: missing untrusted-payload rule")
    if "Do not invent a token" not in text:
        errors.append(f"{name}: missing credential-omit rule")
    errors.extend(audience_errors(name, text))
    if len(text) > MAX_GUIDE:
        errors.append(f"{name}: guide is {len(text)} characters; cap is {MAX_GUIDE}")

    error_part = text.split("## Error codes", 1)[-1].split("## Cases", 1)[0]
    rows = {code: value.lower() == "true" for code, value in CODE_ROW.findall(error_part)}
    if not rows:
        errors.append(f"{name}: error-code table has no rows")
    for code, retryable in rows.items():
        if code not in codes:
            errors.append(f"{name}: `{code}` is not in contract/error-codes.json")
        elif codes[code] != retryable:
            errors.append(f"{name}: `{code}` retryable is {retryable}, file says {codes[code]}")

    cases = case_blocks(text)
    if "```json" not in cases:
        errors.append(f"{name}: ## Cases needs a JSON example")
    if "-32602" not in cases:
        errors.append(f"{name}: ## Cases must describe JSON-RPC -32602")
    for block in FENCE.findall(cases):
        if EXAMPLE_ID in block:
            errors.append(f"{name}: case JSON contains `{EXAMPLE_ID}`")
        found = SECRET_KEY.search(block)
        if found:
            errors.append(f"{name}: case JSON contains `{found.group(1)}`")
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict) or payload.get("success") is not True:
            continue
        if any(isinstance(value, list) for value in payload.values()):
            if "paging" not in payload or "total_page" not in payload:
                errors.append(f"{name}: array success case needs paging and total_page")
    return errors


def dockerfile_path(card: dict) -> Path:
    rel = str(card.get("dockerfile_path") or "./Dockerfile")
    if rel.startswith("/") or ".." in Path(rel).parts:
        fail(["dockerfile_path must stay inside the repository"])
    return (ROOT / rel).resolve()


def dockerfile_instructions(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def dockerfile_errors(card: dict) -> list[str]:
    path = dockerfile_path(card)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return [f"missing {path.name}; replace Dockerfile before publish"]
    errors = []
    if DOCKER_MARKER in text:
        errors.append("replace Dockerfile before publish")
    instructions = dockerfile_instructions(text)
    if not any(line == "USER" or line.startswith("USER ") for line in instructions):
        errors.append("Dockerfile needs a USER instruction (comments do not count)")
    if not any(line.startswith("HEALTHCHECK") for line in instructions):
        errors.append("Dockerfile needs a HEALTHCHECK instruction (comments do not count)")
    exposes = any(line.startswith("EXPOSE") and "8000" in line.split() for line in instructions)
    port_env = any(
        line.startswith("ENV") and "PORT" in line and "8000" in line for line in instructions
    )
    if not exposes and not port_env:
        errors.append("Dockerfile needs EXPOSE 8000 or ENV PORT=8000")
    return errors


def main() -> None:
    publish = "--publish" in sys.argv[1:]
    card = load_json(ROOT / "contract" / "tools.json")
    error_file = load_json(ROOT / "contract" / "error-codes.json")
    errors: list[str] = []

    server_id = str(card.get("server_id") or "")
    tools = card.get("tools")
    if not isinstance(tools, list):
        fail(["contract/tools.json tools must be an array"])

    raw_codes = error_file.get("codes")
    if not isinstance(raw_codes, list) or not raw_codes:
        fail(["contract/error-codes.json codes must be a non-empty array"])
    codes: dict[str, bool] = {}
    for item in raw_codes:
        if not isinstance(item, dict):
            errors.append("error-codes entry is not an object")
            continue
        code = str(item.get("error_code") or "")
        if not code or not isinstance(item.get("retryable"), bool):
            errors.append(f"bad error-code entry: {item!r}")
            continue
        codes[code] = item["retryable"]

    names: list[str] = []
    for tool in tools:
        if isinstance(tool, str):
            names.append(tool)
        elif isinstance(tool, dict) and isinstance(tool.get("name"), str):
            names.append(tool["name"])
        else:
            errors.append(f"tool entry must be a name or {{\"name\": ...}}: {tool!r}")
    for name in names:
        if not NAME_RE.match(name):
            errors.append(f"tool name {name!r} must be snake_case")

    docs = ROOT / "registry_docs"
    guides = sorted(
        path.stem
        for path in docs.glob("*.md")
        if not path.name.startswith("_")
    )
    for name in names:
        path = docs / f"{name}.md"
        if not path.is_file():
            errors.append(f"missing registry_docs/{name}.md")
            continue
        errors.extend(guide_errors(name, path.read_text(encoding="utf-8"), codes))
    for guide in guides:
        if guide not in names:
            errors.append(f"registry_docs/{guide}.md has no matching contract/tools.json entry")

    if names:
        documented: set[str] = set()
        for name in names:
            path = docs / f"{name}.md"
            if not path.is_file():
                continue
            error_part = path.read_text(encoding="utf-8").split("## Error codes", 1)[-1].split("## Cases", 1)[0]
            documented.update(code for code, _ in CODE_ROW.findall(error_part))
        missing = sorted(set(codes) - documented)
        if missing:
            errors.append("error codes never documented: " + ", ".join(missing))

    if publish:
        if server_id.lower() == "replace_server" or not NAME_RE.match(server_id):
            errors.append("set contract/tools.json server_id to a snake_case id before publish")
        if card.get("listen_port") != 8000:
            errors.append("listen_port must stay 8000")
        if card.get("protocol_version") != "2024-11-05":
            errors.append("protocol_version must stay 2024-11-05")
        if card.get("class") != "tool-server":
            errors.append("class must stay tool-server")
        if not names:
            errors.append("declare at least one tool in contract/tools.json")
        placeholder = "One sentence copied onto the Tool Registry publish form."
        if card.get("description") == placeholder or not str(card.get("description") or "").strip():
            errors.append("replace contract/tools.json description")
        errors.extend(dockerfile_errors(card))

    if errors:
        fail(errors)
    if not names:
        print("contract: template only (no tools declared)")
    else:
        print(f"contract: {len(names)} tool(s) ok")


if __name__ == "__main__":
    main()
