"""Check deployment contract behavior through the validator command."""

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
        [uv, "run", "--frozen", "--project", str(WORK), "python", "validate.py", filename],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "UV_PROJECT_ENVIRONMENT": str(WORK / ".venv")},
        check=False,
    )


def test_valid_document_passes() -> None:
    result = _run("valid.json")
    assert result.returncode == 0, result.stderr
    assert "valid:" in result.stdout


def test_missing_required_property_fails_with_path() -> None:
    result = _run("invalid-missing.json")
    assert result.returncode != 0
    assert "replicas" in result.stderr
    assert "required" in result.stderr


def test_wrong_type_fails_with_json_path() -> None:
    result = _run("invalid-type.json")
    assert result.returncode != 0
    assert "$.replicas" in result.stderr


def test_unknown_properties_are_rejected_at_each_object_level() -> None:
    result = _run("invalid-extra.json")
    assert result.returncode != 0
    assert "additional properties" in result.stderr.lower()
    assert "admin_override" in result.stderr


def test_nonstandard_json_constant_is_rejected() -> None:
    result = _run("invalid-nan.json")
    assert result.returncode != 0
    assert "invalid JSON:" in result.stderr
    assert "NaN" in result.stderr


def test_duplicate_object_keys_are_rejected() -> None:
    result = _run("invalid-duplicate-key.json")
    assert result.returncode != 0
    assert "invalid JSON:" in result.stderr
    assert "duplicate" in result.stderr
