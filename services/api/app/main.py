from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .db.models import Base
from .db.session import engine
from .db.models import Org, OrgProfile
from .db.session import SessionLocal
from .routers import runs, onboarding, org, packs, setup, provision


settings = get_settings()

app = FastAPI(title="Agent Swarm API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Org).first() is None:
            org = Org(name="Demo Org", locale_default="en")
            db.add(org)
            db.commit()
            db.refresh(org)
            profile = OrgProfile(org_id=org.id, onboarding_stage=0)
            db.add(profile)
            db.commit()
    finally:
        db.close()


app.include_router(runs.router)
app.include_router(onboarding.router)
app.include_router(org.router)
app.include_router(packs.router)
app.include_router(setup.router)
app.include_router(provision.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
