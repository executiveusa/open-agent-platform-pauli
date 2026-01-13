import json
from pathlib import Path
from jsonschema import Draft7Validator
from app.packs.registry import registry


def test_pack_schema_validation() -> None:
    registry.load()
    assert registry.list()


def test_pack_schema_rejects_invalid() -> None:
    schema_path = Path(__file__).resolve().parents[2] / "app" / "packs" / "pack_schema.json"
    schema = json.loads(schema_path.read_text())
    validator = Draft7Validator(schema)
    bad_pack = {"id": "bad"}
    errors = list(validator.iter_errors(bad_pack))
    assert errors
