# Normalize the service inventory

The platform team consumes a single inventory from tools that emit either
JSON or YAML. They need one predictable JSON file for the next step of the
deployment pipeline.

## Contract

`go run . [--output PATH] INPUT` must:

- read JSON or YAML according to the file extension;
- require a top-level `services` list with `id`, `environment`, `replicas`
  and `expires` on every record;
- trim and lowercase `id` and `environment`, parse `expires` as a calendar
  date, and require `replicas` to be a positive integer (not a boolean);
- sort records by normalized `id`, emit JSON fields in a stable order, and
  write UTF-8 JSON with a final newline;
- reject malformed or invalid input with a useful error and non-zero exit
  status, without creating or replacing the requested output.

## Steps

1. Let Go download the pinned YAML module on the first run.
2. Make the YAML and JSON fixtures produce identical normalized data.
3. Try a record with an invalid replica count and an unsupported file extension.
4. Pre-create an output file, then confirm a failed conversion does not
   change it.
5. Run `dsoxlab check data-json-yaml`.
