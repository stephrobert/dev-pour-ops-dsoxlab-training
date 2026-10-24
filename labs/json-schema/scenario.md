# Write the deployment contract

The `fleetctl` deployment command must reject malformed requests before it
changes a service. `deployment.schema.json` is intentionally too permissive.
Complete it using JSON Schema draft 2020-12.

## Contract

A deployment document has exactly these top-level properties:

- `service`: a non-empty string;
- `version`: a semantic-version-shaped string (`major.minor.patch`);
- `environment`: one of `development`, `staging`, `production`;
- `replicas`: an integer from 1 to 20;
- `strategy`: an object with required `type` (`rolling` or `canary`) and
  optional `max_unavailable` between 0 and 5.

Every object rejects additional properties. `validate.py FILE` prints
`valid: FILE` and exits 0 for a valid document. Invalid JSON or schema data
exits non-zero, gives a readable error, and includes a JSON path for data
validation failures. Enforce RFC 8259 JSON: reject `NaN`, `Infinity`, and
duplicate object keys rather than silently accepting or overwriting them.

## Steps

1. Install the pinned dependency: `uv sync --frozen`.
2. Add the required fields, types, bounds, enums and `additionalProperties`.
3. Check the invalid examples for JSON grammar and schema failures; confirm
   valid input still passes.
4. Run `dsoxlab check json-schema`.
