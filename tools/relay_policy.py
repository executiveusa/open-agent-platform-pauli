import json
from dataclasses import dataclass
from typing import Any


@dataclass
class PolicyResult:
    tier: int
    allow_auto_merge: bool
    reasons: list[str]


def evaluate_policy(payload: dict[str, Any]) -> PolicyResult:
    diff_size = payload.get("diff_size", 0)
    has_migrations = payload.get("has_migrations", False)
    adds_deps = payload.get("adds_dependencies", False)
    touches_auth = payload.get("touches_auth", False)

    if has_migrations or adds_deps or touches_auth:
        return PolicyResult(tier=3, allow_auto_merge=False, reasons=["high_risk_change"])
    if diff_size <= 200:
        return PolicyResult(tier=1, allow_auto_merge=True, reasons=["small_change"])
    if diff_size <= 400:
        return PolicyResult(tier=2, allow_auto_merge=False, reasons=["needs_review"])
    return PolicyResult(tier=3, allow_auto_merge=False, reasons=["large_change"])


if __name__ == "__main__":
    sample = json.loads("""{"diff_size": 120, "has_migrations": false}""")
    result = evaluate_policy(sample)
    print(json.dumps(result.__dict__))
