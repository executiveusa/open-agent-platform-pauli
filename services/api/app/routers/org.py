from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import OrgProfile, Recommendation, OrgConfig, OrgConfigSnapshot
from ..db.utils import get_db


router = APIRouter(prefix="/api/org", tags=["org"], dependencies=[ApiKeyDep])


@router.get("/profile")
async def get_profile(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str | int | None]:
    rate_limiter.check(request)
    profile = db.query(OrgProfile).first()
    if profile is None:
        return {"onboarding_stage": 0, "profile_json": None, "selected_packs": None}
    return {
        "onboarding_stage": profile.onboarding_stage,
        "profile_json": profile.profile_json,
        "selected_packs": profile.selected_packs_json,
    }


@router.get("/recommendations")
async def get_recommendations(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    recs = db.query(Recommendation).order_by(Recommendation.created_at.desc()).limit(10).all()
    return {"items": [{"rec_json": rec.rec_json} for rec in recs]}


@router.get("/config")
async def get_config(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    rate_limiter.check(request)
    config = db.query(OrgConfig).first()
    return {"active_config_json": config.active_config_json if config else None}


@router.get("/config/snapshots")
async def list_snapshots(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    snapshots = db.query(OrgConfigSnapshot).order_by(OrgConfigSnapshot.created_at.desc()).all()
    return {
        "items": [
            {
                "snapshot_id": snap.snapshot_id,
                "config_json": snap.config_json,
                "reason": snap.reason,
                "pack_versions": snap.pack_versions,
                "config_checksum": snap.config_checksum,
            }
            for snap in snapshots
        ]
    }


@router.post("/config/rollback")
async def rollback_snapshot(
    payload: dict[str, str],
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    snapshot_id = payload.get("snapshot_id")
    snapshot = db.query(OrgConfigSnapshot).filter(OrgConfigSnapshot.snapshot_id == snapshot_id).first()
    if snapshot is None:
        return {"status": "missing"}
    config = db.query(OrgConfig).filter(OrgConfig.org_id == snapshot.org_id).first()
    if config is None:
        config = OrgConfig(org_id=snapshot.org_id, active_config_json=snapshot.config_json)
        db.add(config)
    else:
        config.active_config_json = snapshot.config_json
    db.commit()
    return {"status": "rolled_back"}
