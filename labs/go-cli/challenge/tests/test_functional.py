"""Exercise the Go CLI as a caller would."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent / "work"


def _run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    go = shutil.which("go")
    assert go, "Go 1.27.3 is required; install the toolchain declared in go.mod"
    return subprocess.run(
        [go, "run", ".", *args],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, **(env or {})},
        check=False,
    )


def test_help_and_version_are_successful() -> None:
    help_result = _run("help")
    version_result = _run("version")
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout
    assert version_result.returncode == 0
    assert version_result.stdout.strip() == "fleetctl dev"


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


def test_json_file_and_environment_precedence() -> None:
    result = _run(
        "config",
        "show",
        "--config",
        "fleetctl.json",
        env={"FLEETCTL_ENDPOINT": "https://override.example.invalid"},
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "endpoint": "https://override.example.invalid",
        "timeout_seconds": 25,
    }


def test_invalid_timeout_and_unknown_command_fail_clearly() -> None:
    invalid = _run("config", "show", env={"FLEETCTL_TIMEOUT_SECONDS": "0"})
    unknown = _run("deploy")
    assert invalid.returncode != 0
    assert invalid.stderr.strip()
    assert unknown.returncode != 0
    assert unknown.stderr.strip()


def test_standalone_binary_builds_and_runs(tmp_path: Path) -> None:
    go = shutil.which("go")
    assert go, "Go 1.27.3 is required; install the toolchain declared in go.mod"
    binary = tmp_path / "fleetctl"
    build = subprocess.run(
        [go, "build", "-o", str(binary), "."],
        cwd=WORK,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert build.returncode == 0, build.stderr
    result = subprocess.run([str(binary), "version"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert result.stdout.strip() == "fleetctl dev"
