from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import OrgProfile
from ..db.utils import get_db
from ..provisioner.job import run_provisioner, emit_setup_events
import json


router = APIRouter(prefix="/api/provision", tags=["provision"], dependencies=[ApiKeyDep])


class ProvisionPayload(BaseModel):
    org_id: int | None = None


@router.post("/run")
async def provision_run(
    payload: ProvisionPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    org_id = payload.org_id or 1
    profile = db.query(OrgProfile).filter(OrgProfile.org_id == org_id).first()
    selected = []
    if profile and profile.selected_packs_json:
        selected = json.loads(profile.selected_packs_json)
    run_provisioner(db, org_id, selected)
    await emit_setup_events(org_id)
    return {"status": "provisioned"}
