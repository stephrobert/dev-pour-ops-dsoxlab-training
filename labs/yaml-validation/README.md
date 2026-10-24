# Validate a YAML service policy before deployment

The deployment pipeline reads a hand-edited YAML service policy. A parser
alone cannot tell whether the document has the right shape or meets the
operations team's rules.

| | |
|---|---|
| Target | your machine: Python 3, uv |
| Duration | about 45 minutes |
| Network | needed once to install pinned PyYAML and `jsonschema` dependencies |
| Companion lesson | [Validate YAML against a schema](https://www.stephane-robert.info/docs/developper/autres-langages/yaml/valider-schema/) (in French) |

```bash
dsoxlab run yaml-validation
cd labs/yaml-validation/challenge/work
uv sync --frozen
uv run python validate_config.py production.yaml
uv run python validate_config.py policy-error.yaml
dsoxlab check yaml-validation
```

The validator reports syntax, structure, and policy failures distinctly.
Every invalid file returns a non-zero status, suitable for a CI gate.
