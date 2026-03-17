"""Validates JSON data against schemas in data/schemas/."""
import json
import sys
from pathlib import Path

SCHEMA_DIR = Path(__file__).parent.parent / "data" / "schemas"

def validate(data: dict, schema_name: str) -> list[str]:
    """Validate data against a named schema. Returns list of errors (empty = valid)."""
    schema_path = SCHEMA_DIR / f"{schema_name}.json"
    if not schema_path.exists():
        return [f"Schema not found: {schema_name}"]
    schema = json.loads(schema_path.read_text())
    errors = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    return errors

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate_schema.py <schema_name> <json_file>")
        sys.exit(1)
    schema_name = sys.argv[1]
    json_file = sys.argv[2]
    data = json.loads(Path(json_file).read_text())
    errors = validate(data, schema_name)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    print("Valid")
