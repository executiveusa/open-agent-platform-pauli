from datetime import datetime, timedelta
from typing import Any
import json
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import Run, RunStatus, Session as RunSession, OrgProfile
from ..db.utils import get_db
from ..orchestration.events import broker
from ..core.config import get_settings
from ..core.tokens import sign_token


router = APIRouter(prefix="/api/runs", tags=["runs"], dependencies=[ApiKeyDep])


class RunCreate(BaseModel):
    agent_type: str
    inputs: dict[str, Any]
    model: str | None = None


class RunResponse(BaseModel):
    id: int
    run_id: str
    status: RunStatus
    trace_id: str | None
    model_used: str | None
    created_at: datetime


class RunDetail(RunResponse):
    inputs: str | None
    steps: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    failures: list[dict[str, Any]]


class RunList(BaseModel):
    items: list[RunResponse]


class SessionResponse(BaseModel):
    url: str
    token: str
    expires_at: datetime


class StatusUpdate(BaseModel):
    status: RunStatus


@router.post("", response_model=RunResponse)
async def create_run(
    payload: RunCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> RunResponse:
    rate_limiter.check(request)
    settings = get_settings()
    if settings.disable_agent_runs:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent runs disabled by kill switch",
        )
    profile = db.query(OrgProfile).first()
    if profile is None or profile.onboarding_stage < 1:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Onboarding required before creating runs",
        )
    run_id = uuid.uuid4().hex
    trace_id = uuid.uuid4().hex
    run = Run(
        run_id=run_id,
        status=RunStatus.queued,
        trace_id=trace_id,
        model_used=payload.model,
        inputs=str(payload.inputs),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    await broker.publish(run.run_id, {"type": "status", "data": run.status.value})
    return RunResponse(
        id=run.id,
        run_id=run.run_id,
        status=run.status,
        trace_id=run.trace_id,
        model_used=run.model_used,
        created_at=run.created_at,
    )


@router.get("", response_model=RunList)
async def list_runs(
    request: Request,
    db: Session = Depends(get_db),
) -> RunList:
    rate_limiter.check(request)
    runs = db.query(Run).order_by(Run.created_at.desc()).limit(50).all()
    return RunList(
        items=[
            RunResponse(
                id=run.id,
                run_id=run.run_id,
                status=run.status,
                trace_id=run.trace_id,
                model_used=run.model_used,
                created_at=run.created_at,
            )
            for run in runs
        ]
    )


@router.get("/{run_id}", response_model=RunDetail)
async def get_run(
    run_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> RunDetail:
    rate_limiter.check(request)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if not run:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return RunDetail(
        id=run.id,
        run_id=run.run_id,
        status=run.status,
        trace_id=run.trace_id,
        model_used=run.model_used,
        created_at=run.created_at,
        inputs=run.inputs,
        steps=[
            {
                "order": step.step_order,
                "status": step.status,
                "tool": step.tool,
                "inputs": step.inputs,
                "outputs": step.outputs,
                "created_at": step.created_at,
            }
            for step in run.steps
        ],
        artifacts=[{"name": art.name, "url": art.url} for art in run.artifacts],
        failures=[
            {
                "error": failure.error,
                "stack": failure.stack,
                "metadata": failure.metadata,
                "screenshot_url": failure.screenshot_url,
                "created_at": failure.created_at,
            }
            for failure in run.failures
        ],
    )


@router.get("/{run_id}/events")
async def run_events(
    run_id: str,
    request: Request,
) -> StreamingResponse:
    rate_limiter.check(request)

    async def event_generator():
        yield "event: status\ndata: CONNECTED\n\n"
        async for payload in broker.stream(run_id):
            event_type = payload.get("type", "message")
            data = payload.get("data") if "data" in payload else payload
            if event_type == "status" and isinstance(data, str):
                yield f"event: status\ndata: {data}\n\n"
            else:
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{run_id}/approve")
async def approve_run(
    run_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.status = RunStatus.running
        db.commit()
        await broker.publish(run.run_id, {"type": "status", "data": run.status.value})
    return {"status": "approved"}


@router.post("/{run_id}/status")
async def update_run_status(
    run_id: str,
    payload: StatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.status = payload.status
        db.commit()
        await broker.publish(run.run_id, {"type": "status", "data": run.status.value})
    return {"status": payload.status.value}


@router.post("/{run_id}/cancel")
async def cancel_run(
    run_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.status = RunStatus.canceled
        db.commit()
        await broker.publish(run.run_id, {"type": "status", "data": run.status.value})
    return {"status": "canceled"}


@router.post("/{run_id}/heal")
async def heal_run(
    run_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run:
        run.status = RunStatus.running
        db.commit()
        await broker.publish(run.run_id, {"type": "heal", "data": run.status.value})
    return {"status": "healing"}


@router.get("/{run_id}/session", response_model=SessionResponse)
async def get_session(
    run_id: str,
    request: Request,
    db: Session = Depends(get_db),
) -> SessionResponse:
    rate_limiter.check(request)
    settings = get_settings()
    token = uuid.uuid4().hex
    signed_token = sign_token(token)
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    run = db.query(Run).filter(Run.run_id == run_id).first()
    if run is None:
        run = Run(run_id=run_id, status=RunStatus.queued)
        db.add(run)
        db.commit()
        db.refresh(run)
    session = RunSession(
        run_id=run.id,
        token=token,
        expires_at=expires_at,
        novnc_url=f"http://localhost:6080/vnc.html?token={signed_token}",
    )
    db.add(session)
    db.commit()
    await broker.publish(run_id, {"type": "session", "data": {"url": session.novnc_url}})
    return SessionResponse(url=session.novnc_url, token=signed_token, expires_at=expires_at)
