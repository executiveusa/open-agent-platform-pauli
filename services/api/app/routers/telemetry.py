import json
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import TelemetryEvent, OrgMetricsDaily, PackMetricsDaily
from ..db.utils import get_db


router = APIRouter(prefix="/api/telemetry", tags=["telemetry"], dependencies=[ApiKeyDep])


class TelemetryPayload(BaseModel):
    org_id: int
    ts: str
    type: str
    pack_ids: list[str] | None = None
    payload: dict[str, object] | None = None
    privacy: dict[str, object] | None = None
    schema_version: str = "1"


@router.post("/event")
async def record_event(
    payload: TelemetryPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    event = TelemetryEvent(
        org_id=payload.org_id,
        event_type=payload.type,
        pack_ids=json.dumps(payload.pack_ids or []),
        payload_json=json.dumps(payload.payload or {}),
        privacy_json=json.dumps(payload.privacy or {}),
        schema_version=payload.schema_version,
    )
    db.add(event)
    db.commit()
    return {"status": "recorded"}


@router.get("/org-summary")
async def org_summary(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    metrics = db.query(OrgMetricsDaily).limit(30).all()
    return {"items": [{"metrics_json": metric.metrics_json} for metric in metrics]}


@router.get("/pack-summary")
async def pack_summary(
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, list[dict[str, str]]]:
    rate_limiter.check(request)
    metrics = db.query(PackMetricsDaily).limit(30).all()
    return {"items": [{"metrics_json": metric.metrics_json} for metric in metrics]}
