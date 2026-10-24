"""Validate YAML syntax, document structure, and service policy."""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_config.py FILE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"syntax: {exc}", file=sys.stderr)
        return 2
    try:
        schema = json.loads(Path("service.schema.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"schema: {exc}", file=sys.stderr)
        return 2
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        print(f"schema: {exc.message}", file=sys.stderr)
        return 2
    errors = sorted(
        Draft202012Validator(schema).iter_errors(document),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if errors:
        for error in errors:
            location = "$" + "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in error.absolute_path
            )
            print(f"structure: {location}: {error.message}", file=sys.stderr)
        return 1
    if document["environment"] == "production" and document["replicas"] < 2:
        print("policy: production services require at least 2 replicas", file=sys.stderr)
        return 1
    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
