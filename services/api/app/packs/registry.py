import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from jsonschema import Draft7Validator


PACKS_ROOT = Path(__file__).resolve().parents[4] / "packs"
SCHEMA_PATH = Path(__file__).resolve().parent / "pack_schema.json"


@dataclass
class Pack:
    pack_id: str
    version: str
    pack_type: str
    locales: list[str]
    pack_json: dict[str, Any]
    onboarding_json: dict[str, Any]
    defaults_json: dict[str, Any]
    workflows_json: dict[str, Any]
    policies_json: dict[str, Any]
    copy_json: dict[str, Any]


class PackRegistry:
    def __init__(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text())
        self.validator = Draft7Validator(schema)
        self._packs: dict[str, Pack] = {}

    def load(self) -> None:
        self._packs = {}
        if not PACKS_ROOT.exists():
            return
        for pack_dir in sorted(PACKS_ROOT.iterdir()):
            if not pack_dir.is_dir():
                continue
            pack_json = json.loads((pack_dir / "pack.json").read_text())
            errors = sorted(self.validator.iter_errors(pack_json), key=lambda e: e.path)
            if errors:
                raise ValueError(f"Invalid pack.json in {pack_dir.name}: {errors[0].message}")
            pack = Pack(
                pack_id=pack_json["id"],
                version=pack_json["version"],
                pack_type=pack_json["type"],
                locales=pack_json["locales"],
                pack_json=pack_json,
                onboarding_json=json.loads((pack_dir / "onboarding.json").read_text()),
                defaults_json=json.loads((pack_dir / "defaults.json").read_text()),
                workflows_json=json.loads((pack_dir / "workflows.json").read_text()),
                policies_json=json.loads((pack_dir / "policies.json").read_text()),
                copy_json=json.loads((pack_dir / "copy.json").read_text()),
            )
            self._packs[pack.pack_id] = pack

    def list(self) -> list[Pack]:
        return list(self._packs.values())

    def get(self, pack_id: str) -> Pack | None:
        return self._packs.get(pack_id)


registry = PackRegistry()
