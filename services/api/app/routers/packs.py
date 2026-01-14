from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.utils import get_db
from ..db.models import OrgProfile
import json
from ..packs.registry import registry


router = APIRouter(prefix="/api/packs", tags=["packs"], dependencies=[ApiKeyDep])


class PackSelection(BaseModel):
    pack_ids: list[str]


@router.get("")
async def list_packs(request: Request) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    registry.load()
    return {
        "items": [
            {"id": pack.pack_id, "version": pack.version, "type": pack.pack_type}
            for pack in registry.list()
        ]
    }


@router.get("/{pack_id}")
async def get_pack(pack_id: str, request: Request) -> dict[str, object]:
    rate_limiter.check(request)
    registry.load()
    pack = registry.get(pack_id)
    if pack is None:
        return {"status": "missing"}
    return {
        "pack_json": pack.pack_json,
        "onboarding_json": pack.onboarding_json,
        "defaults_json": pack.defaults_json,
        "workflows_json": pack.workflows_json,
        "policies_json": pack.policies_json,
        "copy_json": pack.copy_json,
    }


@router.post("/select")
async def select_pack(
    payload: PackSelection,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    profile = db.query(OrgProfile).first()
    if profile is None:
        return {"status": "missing"}
    profile.selected_packs_json = json.dumps(payload.pack_ids)
    db.commit()
    return {"status": "selected"}
