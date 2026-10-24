"""Validate syntax, schema, and policy behavior through the CLI."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent / "work"


def _run(filename: str) -> subprocess.CompletedProcess[str]:
    uv = shutil.which("uv")
    assert uv, "uv is required; run mise install"
    return subprocess.run(
        [uv, "run", "--frozen", "--project", str(WORK), "python", "validate_config.py", filename],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(WORK / ".venv")},
        check=False,
    )


def test_valid_production_configuration_passes() -> None:
    result = _run("production.yaml")
    assert result.returncode == 0, result.stderr
    assert "valid:" in result.stdout


def test_yaml_syntax_error_is_classified() -> None:
    result = _run("syntax-error.yaml")
    assert result.returncode != 0
    assert "syntax:" in result.stderr
    assert "Traceback" not in result.stderr


def test_schema_error_reports_structure_and_property() -> None:
    result = _run("structure-error.yaml")
    assert result.returncode != 0
    assert "structure:" in result.stderr
    assert "$.environment" in result.stderr or "$.replicas" in result.stderr


def test_production_policy_failure_is_distinct() -> None:
    result = _run("policy-error.yaml")
    assert result.returncode != 0
    assert "policy:" in result.stderr
    assert "replicas" in result.stderr


def test_malformed_schema_fails_with_schema_diagnostic() -> None:
    schema = WORK / "service.schema.json"
    original = schema.read_text(encoding="utf-8")
    try:
        schema.write_text('{"type": 7}\n', encoding="utf-8")
        result = _run("production.yaml")
    finally:
        schema.write_text(original, encoding="utf-8")
    assert result.returncode != 0
    assert "schema:" in result.stderr
