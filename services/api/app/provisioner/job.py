import json
from datetime import datetime
from sqlalchemy.orm import Session
from ..packs.registry import registry
from .merge import merge_configs
from ..db.models import OrgConfig, OrgConfigSnapshot, OrgProfile, Recommendation
from ..orchestration.events import broker


def run_provisioner(db: Session, org_id: int, selected_packs: list[str]) -> dict[str, str]:
    registry.load()
    packs = []
    for pack_id in selected_packs:
        pack = registry.get(pack_id)
        if pack:
            packs.append(
                {
                    "pack_json": pack.pack_json,
                    "defaults_json": pack.defaults_json,
                    "workflows_json": pack.workflows_json,
                    "policies_json": pack.policies_json,
                }
            )
    config = merge_configs(packs)
    org_config = db.query(OrgConfig).filter(OrgConfig.org_id == org_id).first()
    if org_config is None:
        org_config = OrgConfig(org_id=org_id, active_config_json=json.dumps(config))
        db.add(org_config)
    else:
        org_config.active_config_json = json.dumps(config)
    snapshot = OrgConfigSnapshot(
        org_id=org_id,
        snapshot_id=f"snap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        config_json=json.dumps(config),
        reason="provisioner",
        pack_versions=json.dumps(config.get("pack_versions", {})),
    )
    db.add(snapshot)
    recommendation = Recommendation(
        org_id=org_id,
        rec_json=json.dumps(
            {
                "packs": selected_packs,
                "quick_actions": config.get("quick_actions", []),
                "workflows": config.get("workflows", []),
            }
        ),
    )
    db.add(recommendation)
    db.commit()
    return {"status": "ok", "snapshot_id": snapshot.snapshot_id}


async def emit_setup_events(org_id: int) -> None:
    await broker.publish(f"setup-{org_id}", {"type": "status", "data": "PROVISIONING"})
    await broker.publish(f"setup-{org_id}", {"type": "status", "data": "CONFIG_READY"})
    await broker.publish(f"setup-{org_id}", {"type": "status", "data": "DONE"})
