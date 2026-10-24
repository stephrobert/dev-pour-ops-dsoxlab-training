# Enforce a deployment contract with JSON Schema

A deployment tool consumes JSON edited by several teams. Enforce the JSON
grammar as well as a JSON Schema contract, rejecting ambiguous or unexpected
data before deployment.

| | |
|---|---|
| Target | your machine: Python 3, uv |
| Duration | about 45 minutes |
| Network | needed once to install the pinned `jsonschema` dependency |
| Companion lesson | [Write a JSON Schema](https://www.stephane-robert.info/docs/developper/autres-langages/json/ecrire-un-schema/) (in French) |

```bash
dsoxlab run json-schema
cd labs/json-schema/challenge/work
uv sync --frozen
uv run python validate.py valid.json
uv run python validate.py invalid-extra.json
dsoxlab check json-schema
```

The grader tests strict JSON parsing, valid input, missing fields, wrong
types, unknown fields, and JSON paths in validation errors. It evaluates
behavior, not schema formatting.
