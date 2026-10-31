"""Locks scripts/check_contract.py. The MCP server itself may use any language."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(tree: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(tree / "scripts" / "check_contract.py"), *args],
        cwd=tree,
        capture_output=True,
        text=True,
    )


def filled_card() -> dict:
    return {
        "server_id": "acme",
        "display_name": "Acme MCP",
        "description": "Lists items for the connected account.",
        "listen_port": 8000,
        "health_path": "/health",
        "mcp_path": "/mcp",
        "protocol_version": "2024-11-05",
        "class": "tool-server",
        "dockerfile_path": "./Dockerfile",
        "tools": ["list_items"],
    }


def real_dockerfile() -> str:
    return """FROM alpine:3.20
ENV PORT=8000
EXPOSE 8000
USER nobody
HEALTHCHECK CMD wget -q -O- http://127.0.0.1:8000/health || exit 1
CMD ["echo", "replace-with-server"]
"""


class CheckContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tree = Path(self.tmp.name) / "mcp-tool"
        shutil.copytree(ROOT, self.tree, ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_template_is_not_publishable(self) -> None:
        plain = run(self.tree)
        self.assertEqual(plain.returncode, 0, plain.stderr)
        self.assertIn("template only", plain.stdout)
        publish = run(self.tree, "--publish")
        self.assertEqual(publish.returncode, 1)
        self.assertIn("server_id", publish.stderr)
        self.assertIn("at least one tool", publish.stderr)
        self.assertIn("replace Dockerfile", publish.stderr)
        self.assertNotIn("Traceback", publish.stderr)

    def test_comment_only_image_fails_publish(self) -> None:
        self._declare_tool()
        (self.tree / "Dockerfile").write_text(
            "# USER nobody\n# HEALTHCHECK CMD true\n# EXPOSE 8000\nFROM alpine:3.20\n",
            encoding="utf-8",
        )
        result = run(self.tree, "--publish")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("USER instruction", result.stderr)
        self.assertIn("HEALTHCHECK instruction", result.stderr)

    def test_hollow_guide_and_secret_case_fail(self) -> None:
        self._declare_tool()
        (self.tree / "Dockerfile").write_text(real_dockerfile(), encoding="utf-8")
        hollow = "\n".join(
            [
                "# list_items",
                "## Agent rules",
                "untrusted",
                "Do not invent a token",
                "## When to call",
                "## Parameters",
                "| Name | Required | Type | Sample | Related tool | Meaning |",
                "## Success fields",
                "## Error codes",
                "## Cases",
                "```json",
                '{"password": "s3cret", "token": "ya29.live"}',
                "```",
            ]
        )
        (self.tree / "registry_docs" / "list_items.md").write_text(hollow + "\n", encoding="utf-8")
        result = run(self.tree, "--publish")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("parameter table has no rows", result.stderr)
        self.assertIn("missing ## Audience", result.stderr)
        self.assertIn("-32602", result.stderr)
        self.assertIn("password", result.stderr)

    def test_anonymous_with_a_token_fails(self) -> None:
        self._declare_tool()
        (self.tree / "Dockerfile").write_text(real_dockerfile(), encoding="utf-8")
        guide = (self.tree / "registry_docs" / "list_items.md").read_text(encoding="utf-8")
        guide = guide.replace("| external | required |", "| anonymous | required |", 1)
        (self.tree / "registry_docs" / "list_items.md").write_text(guide, encoding="utf-8")
        result = run(self.tree, "--publish")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("anonymous cannot require an authentication token", result.stderr)

    def test_false_retryable_cell_is_accepted(self) -> None:
        self._declare_tool()
        (self.tree / "Dockerfile").write_text(real_dockerfile(), encoding="utf-8")
        guide = (self.tree / "registry_docs" / "list_items.md").read_text(encoding="utf-8")
        guide = guide.replace("| `CREDENTIALS_REQUIRED` | false |", "| `CREDENTIALS_REQUIRED` | False |", 1)
        (self.tree / "registry_docs" / "list_items.md").write_text(guide, encoding="utf-8")
        result = run(self.tree, "--publish")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 tool(s) ok", result.stdout)

    def test_register_docs_required(self) -> None:
        contract = (self.tree / "CONTRACT.md").read_text(encoding="utf-8")
        (self.tree / "CONTRACT.md").write_text(
            contract.replace("GET /register", "GET /health"),
            encoding="utf-8",
        )
        result = run(self.tree)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("GET /register", result.stderr)

    def test_replace_server_and_missing_dockerfile(self) -> None:
        card = filled_card()
        card["server_id"] = "replace_server"
        (self.tree / "contract" / "tools.json").write_text(json.dumps(card), encoding="utf-8")
        guide = (self.tree / "registry_docs" / "_template.md").read_text(encoding="utf-8")
        (self.tree / "registry_docs" / "list_items.md").write_text(guide, encoding="utf-8")
        (self.tree / "Dockerfile").write_text(real_dockerfile(), encoding="utf-8")
        bad_id = run(self.tree, "--publish")
        self.assertEqual(bad_id.returncode, 1)
        self.assertIn("server_id", bad_id.stderr)

        card["server_id"] = "acme"
        (self.tree / "contract" / "tools.json").write_text(json.dumps(card), encoding="utf-8")
        (self.tree / "Dockerfile").unlink()
        missing = run(self.tree, "--publish")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("missing", missing.stderr.lower())
        self.assertNotIn("Traceback", missing.stderr)

    def _declare_tool(self) -> None:
        (self.tree / "contract" / "tools.json").write_text(
            json.dumps(filled_card(), indent=2) + "\n",
            encoding="utf-8",
        )
        guide = (self.tree / "registry_docs" / "_template.md").read_text(encoding="utf-8")
        (self.tree / "registry_docs" / "list_items.md").write_text(guide, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
