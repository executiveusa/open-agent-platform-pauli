import json
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import OrgPackInstall, OrgProfile
from ..db.utils import get_db
from ..packs.registry import registry
from ..provisioner.job import run_provisioner


router = APIRouter(prefix="/api/marketplace", tags=["marketplace"], dependencies=[ApiKeyDep])


class PackAction(BaseModel):
    pack_id: str


@router.get("/packs")
async def list_marketplace_packs(request: Request) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    registry.load()
    return {
        "items": [
            {"pack_id": pack.pack_id, "version": pack.version, "type": pack.pack_type}
            for pack in registry.list()
        ]
    }


@router.get("/packs/{pack_id}")
async def get_marketplace_pack(pack_id: str, request: Request) -> dict[str, object]:
    rate_limiter.check(request)
    registry.load()
    pack = registry.get(pack_id)
    if pack is None:
        return {"status": "missing"}
    return {
        "pack_json": pack.pack_json,
        "defaults_json": pack.defaults_json,
        "copy_json": pack.copy_json,
    }


@router.post("/install")
async def install_pack(
    payload: PackAction,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    install = OrgPackInstall(org_id=1, pack_id=payload.pack_id, status="enabled")
    db.add(install)
    db.commit()
    profile = db.query(OrgProfile).filter(OrgProfile.org_id == 1).first()
    selected = []
    if profile and profile.selected_packs_json:
        selected = json.loads(profile.selected_packs_json)
    if payload.pack_id not in selected:
        selected.append(payload.pack_id)
    if profile:
        profile.selected_packs_json = json.dumps(selected)
    run_provisioner(db, 1, selected)
    return {"status": "installed"}


@router.post("/enable")
async def enable_pack(
    payload: PackAction,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    install = db.query(OrgPackInstall).filter(OrgPackInstall.pack_id == payload.pack_id).first()
    if install:
        install.status = "enabled"
        db.commit()
    profile = db.query(OrgProfile).filter(OrgProfile.org_id == 1).first()
    if profile and profile.selected_packs_json:
        selected = json.loads(profile.selected_packs_json)
        if payload.pack_id not in selected:
            selected.append(payload.pack_id)
        profile.selected_packs_json = json.dumps(selected)
        run_provisioner(db, 1, selected)
    return {"status": "enabled"}


@router.post("/disable")
async def disable_pack(
    payload: PackAction,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    install = db.query(OrgPackInstall).filter(OrgPackInstall.pack_id == payload.pack_id).first()
    if install:
        install.status = "disabled"
        db.commit()
    profile = db.query(OrgProfile).filter(OrgProfile.org_id == 1).first()
    if profile and profile.selected_packs_json:
        selected = [pack for pack in json.loads(profile.selected_packs_json) if pack != payload.pack_id]
        profile.selected_packs_json = json.dumps(selected)
        run_provisioner(db, 1, selected)
    return {"status": "disabled"}


@router.get("/recommended")
async def recommended_packs(request: Request) -> dict[str, list[str]]:
    rate_limiter.check(request)
    return {"items": ["dentist-core", "bookings-growth"]}
