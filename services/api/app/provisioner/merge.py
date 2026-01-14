from typing import Any


def merge_configs(
    base_defaults: dict[str, Any],
    packs: list[dict[str, Any]],
    org_overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "layout": {"tabs": []},
        "quick_actions": [],
        "workflows": [],
        "policies": {},
        "pack_versions": {},
    }
    merged["layout"].update(base_defaults.get("layout", {}))
    merged["quick_actions"].extend(base_defaults.get("quick_actions", []))
    for pack in packs:
        pack_id = pack["pack_json"]["id"]
        merged["pack_versions"][pack_id] = pack["pack_json"]["version"]
        defaults = pack.get("defaults_json", {})
        workflows = pack.get("workflows_json", {})
        policies = pack.get("policies_json", {})
        if "layout" in defaults:
            merged["layout"].update(defaults["layout"])
        merged["quick_actions"].extend(defaults.get("quick_actions", []))
        merged["workflows"].extend(workflows.get("workflows", []))
        merged["policies"].update(policies)
    if org_overrides:
        merged["layout"].update(org_overrides.get("layout", {}))
        merged["quick_actions"].extend(org_overrides.get("quick_actions", []))
    merged["layout"]["tabs"] = list(dict.fromkeys(merged["layout"].get("tabs", [])))
    merged["quick_actions"] = list(dict.fromkeys(merged["quick_actions"]))
    return merged
