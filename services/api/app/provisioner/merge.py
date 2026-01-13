from typing import Any


def merge_configs(packs: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {
        "layout": {"tabs": []},
        "quick_actions": [],
        "workflows": [],
        "policies": {},
        "pack_versions": {},
    }
    for pack in sorted(packs, key=lambda item: item["pack_json"]["id"]):
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
    merged["layout"]["tabs"] = list(dict.fromkeys(merged["layout"].get("tabs", [])))
    merged["quick_actions"] = list(dict.fromkeys(merged["quick_actions"]))
    return merged
