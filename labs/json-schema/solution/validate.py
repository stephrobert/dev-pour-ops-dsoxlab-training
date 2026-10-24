#!/usr/bin/env python3
"""Validate a deployment JSON document strictly against its schema."""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate object key: {key}")
        document[key] = value
    return document


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def _load_strict_json(path: Path) -> object:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_object_without_duplicate_keys,
        parse_constant=_reject_nonstandard_constant,
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate.py FILE", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        schema = _load_strict_json(Path("deployment.schema.json"))
    except (OSError, ValueError) as exc:
        print(f"invalid schema JSON: {exc}", file=sys.stderr)
        return 2
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        print(f"invalid schema: {exc.message}", file=sys.stderr)
        return 2
    try:
        document = _load_strict_json(path)
    except (OSError, ValueError) as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
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
            print(f"{location}: {error.message}", file=sys.stderr)
        return 1
    print(f"valid: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
