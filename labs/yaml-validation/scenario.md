# Validate service policy in three layers

The deployment pipeline must not confuse unreadable YAML with a readable
document that violates its contract or an operations rule. Complete
`validate_config.py` and `service.schema.json`.

## Contract

`validate_config.py FILE` must perform these checks in order:

1. **Syntax:** parse one YAML document safely. On a parse or file error,
   print a `syntax:` diagnostic and exit non-zero.
2. **Structure:** validate the document against `service.schema.json`.
   Required fields are `service` (non-empty string), `environment`
   (`staging` or `production`), and `replicas` (integer from 1 to 20).
   Unknown keys are rejected. Report a `structure:` diagnostic and the
   invalid property path.
3. **Policy:** production services require at least two replicas. Report a
   `policy:` diagnostic when this rule is broken.

Print `valid: FILE` and exit 0 only when every layer passes. Do not emit a
traceback for input errors.

## Steps

1. Run `uv sync --frozen`.
2. Complete the JSON Schema, including `additionalProperties: false`.
3. Implement safe parsing, schema validation, then the production rule.
4. Try each fixture and run `dsoxlab check yaml-validation`.
