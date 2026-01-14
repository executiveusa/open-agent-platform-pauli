import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.config import get_settings as get_app_settings
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import AuditLog, OrgSettings
from ..db.utils import get_db


router = APIRouter(prefix="/api/org/settings", tags=["org-settings"], dependencies=[ApiKeyDep])


class AutonomyPayload(BaseModel):
    mode: str
    reason: str
    duration_hours: int | None = 2
    confirmation: str | None = None


@router.get("")
async def get_settings(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    rate_limiter.check(request)
    settings = db.query(OrgSettings).first()
    force_mode = get_app_settings().force_autonomy_mode
    app_settings = get_app_settings()
    return {
        "autonomy_mode": force_mode or (settings.autonomy_mode if settings else "tiered"),
        "fuck_it_expires_at": settings.fuck_it_expires_at.isoformat()
        if settings and settings.fuck_it_expires_at
        else None,
        "disable_agent_runs": app_settings.disable_agent_runs,
        "disable_automerge": app_settings.disable_automerge,
    }


@router.post("/autonomy")
async def update_autonomy(
    payload: AutonomyPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    settings = db.query(OrgSettings).first()
    if settings is None:
        settings = OrgSettings(org_id=1)
        db.add(settings)
    if payload.mode == "fuck_it" and payload.confirmation != "FUCK IT MODE":
        return {"status": "confirmation_required"}
    settings.autonomy_mode = payload.mode
    if payload.mode == "fuck_it":
        settings.fuck_it_expires_at = datetime.utcnow() + timedelta(hours=payload.duration_hours or 2)
    else:
        settings.fuck_it_expires_at = None
    audit = AuditLog(
        org_id=1,
        actor="admin",
        action="autonomy_mode_changed",
        details_json=json.dumps({"mode": payload.mode, "reason": payload.reason}),
    )
    db.add(audit)
    db.commit()
    return {"status": "updated"}
