"""Validate YAML syntax, document structure, and service policy."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_config.py FILE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2

    schema = json.loads(Path("service.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(document))
    if errors:
        print(f"structure: {errors[0].message}", file=sys.stderr)
        return 1
    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
