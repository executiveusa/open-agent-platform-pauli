from typing import Any


class PackSelectionResult:
    def __init__(self, pack_ids: list[str], confidence: float) -> None:
        self.pack_ids = pack_ids
        self.confidence = confidence


RULES = {
    "industry": {
        "dentist": "dentist-core",
        "real_estate": "real-estate-core",
        "agency": "agency-core",
    },
    "primary_goal": {
        "bookings": "bookings-growth",
        "leads": "leads-growth",
    },
    "primary_channel": {
        "whatsapp": "whatsapp-first",
        "instagram": "instagram-first",
    },
}


def select_packs(answers: dict[str, Any]) -> PackSelectionResult:
    selected: list[str] = []
    hits = 0
    total = 0
    for key, mapping in RULES.items():
        total += 1
        value = answers.get(key)
        if value in mapping:
            selected.append(mapping[value])
            hits += 1
    confidence = hits / total if total else 0.0
    return PackSelectionResult(pack_ids=selected, confidence=confidence)
