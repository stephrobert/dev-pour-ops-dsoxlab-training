"""Observe the Go normalizer only through its command-line interface."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent / "work"
EXPECTED = [
    {"id": "api", "environment": "production", "replicas": 3, "expires": "2026-12-20"},
    {"id": "web", "environment": "staging", "replicas": 2, "expires": "2026-11-30"},
]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    go = shutil.which("go")
    assert go, "Go 1.27.3 is required; install the toolchain declared in go.mod"
    return subprocess.run(
        [go, "run", ".", *args],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=120,
        env=os.environ.copy(),
        check=False,
    )


def test_json_and_yaml_have_the_same_canonical_output() -> None:
    yaml_result = _run("inventory.yaml")
    json_result = _run("inventory.json")
    assert yaml_result.returncode == json_result.returncode == 0
    assert json.loads(yaml_result.stdout) == json.loads(json_result.stdout) == EXPECTED
    assert yaml_result.stdout == json_result.stdout
    assert yaml_result.stdout.endswith("\n")


def test_invalid_record_is_rejected_without_touching_output(tmp_path: Path) -> None:
    output = tmp_path / "existing.json"
    output.write_text("keep me\n", encoding="utf-8")
    result = _run("--output", str(output), "invalid.yaml")
    assert result.returncode != 0
    assert result.stderr.strip()
    assert output.read_text(encoding="utf-8") == "keep me\n"


def test_unknown_format_is_rejected() -> None:
    result = _run("unsupported.toml")
    assert result.returncode != 0
    assert "unsupported" in result.stderr.lower()


def test_go_unit_tests_pass() -> None:
    go = shutil.which("go")
    assert go, "Go 1.27.3 is required; install the toolchain declared in go.mod"
    result = subprocess.run(
        [go, "test", "./..."],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
