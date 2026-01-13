from app.provisioner.merge import merge_configs


def test_merge_deterministic() -> None:
    packs = [
        {
            "pack_json": {"id": "b", "version": "1.0.0"},
            "defaults_json": {"layout": {"tabs": ["B"]}, "quick_actions": ["q2"]},
            "workflows_json": {"workflows": [{"id": "w2"}]},
            "policies_json": {"safe_mode": True},
        },
        {
            "pack_json": {"id": "a", "version": "1.0.0"},
            "defaults_json": {"layout": {"tabs": ["A"]}, "quick_actions": ["q1"]},
            "workflows_json": {"workflows": [{"id": "w1"}]},
            "policies_json": {"restricted_actions": ["x"]},
        },
    ]
    first = merge_configs(packs)
    second = merge_configs(list(reversed(packs)))
    assert first == second
