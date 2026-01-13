import json
from datetime import datetime
from pathlib import Path
from typing import Any
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..db.models import (
    OnboardingAnswer,
    OnboardingSession,
    Org,
    OrgProfile,
)
from ..db.utils import get_db
from ..provisioner.classifier import select_packs
from ..provisioner.job import emit_setup_events, run_provisioner


router = APIRouter(prefix="/api/onboarding", tags=["onboarding"], dependencies=[ApiKeyDep])
TEMPLATE_PATH = Path(__file__).resolve().parents[4] / "config" / "onboarding" / "default-v1.json"


class SessionStart(BaseModel):
    locale: str
    persona: dict[str, Any] | None = None
    org_name: str | None = None


class AnswerPayload(BaseModel):
    question_id: str
    answer: dict[str, Any] | str


class FinalizePayload(BaseModel):
    session_id: int


@router.get("/template")
async def get_template(
    request: Request,
) -> dict[str, Any]:
    rate_limiter.check(request)
    return json.loads(TEMPLATE_PATH.read_text())


@router.post("/session/start")
async def start_session(
    payload: SessionStart,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rate_limiter.check(request)
    org = db.query(Org).first()
    if org is None:
        org = Org(name=payload.org_name or "Demo Org", locale_default=payload.locale)
        db.add(org)
        db.commit()
        db.refresh(org)
        profile = OrgProfile(org_id=org.id, onboarding_stage=0)
        db.add(profile)
        db.commit()
    session = OnboardingSession(
        org_id=org.id,
        status="active",
        locale=payload.locale,
        persona_json=json.dumps(payload.persona or {}),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "org_id": org.id}


@router.post("/session/{session_id}/answer")
async def store_answer(
    session_id: int,
    payload: AnswerPayload,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    answer = OnboardingAnswer(
        session_id=session_id,
        question_id=payload.question_id,
        answer_json=json.dumps(payload.answer),
    )
    db.add(answer)
    db.commit()
    return {"status": "saved"}


@router.post("/session/{session_id}/confirm")
async def confirm_session(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    rate_limiter.check(request)
    session = db.query(OnboardingSession).filter(OnboardingSession.id == session_id).first()
    if session:
        session.status = "confirmed"
        db.commit()
    return {"status": "confirmed"}


@router.post("/session/{session_id}/finalize")
async def finalize_session(
    session_id: int,
    request: Request,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rate_limiter.check(request)
    session = db.query(OnboardingSession).filter(OnboardingSession.id == session_id).first()
    if session is None:
        return {"status": "missing"}
    answers = db.query(OnboardingAnswer).filter(OnboardingAnswer.session_id == session_id).all()
    answers_dict = {answer.question_id: json.loads(answer.answer_json) for answer in answers}
    template = json.loads(TEMPLATE_PATH.read_text())
    min_fields = template.get("min_stage_fields", [])
    missing_fields = [field for field in min_fields if field not in answers_dict or not answers_dict[field]]
    selection = select_packs(answers_dict)
    profile = db.query(OrgProfile).filter(OrgProfile.org_id == session.org_id).first()
    if profile is None:
        profile = OrgProfile(org_id=session.org_id)
        db.add(profile)
    profile.profile_json = json.dumps(answers_dict)
    profile.selected_packs_json = json.dumps(selection.pack_ids)
    if missing_fields:
        profile.onboarding_stage = 0
    else:
        profile.onboarding_stage = 1
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    if profile.onboarding_stage >= 1:
        run_provisioner(db, session.org_id, selection.pack_ids)
        await emit_setup_events(session.org_id)
    return {
        "status": "completed" if not missing_fields else "incomplete",
        "onboarding_stage": profile.onboarding_stage,
        "selected_packs": selection.pack_ids,
        "confidence": selection.confidence,
        "missing_fields": missing_fields,
    }


@router.post("/stt")
async def speech_to_text(
    request: Request,
) -> dict[str, str]:
    rate_limiter.check(request)
    return {"transcript": ""}
