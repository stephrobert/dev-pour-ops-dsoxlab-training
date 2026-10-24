#!/usr/bin/env python3
"""Validate a deployment JSON document against deployment.schema.json."""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate.py FILE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        schema = json.loads(Path("deployment.schema.json").read_text(encoding="utf-8"))
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 2
    errors = list(Draft202012Validator(schema).iter_errors(document))
    if errors:
        print(f"invalid: {errors[0].message}", file=sys.stderr)
        return 1
    print(f"document accepted: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
