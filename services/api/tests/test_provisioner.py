import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base, Org, OrgProfile, OrgConfigSnapshot, OrgConfig
from app.provisioner.job import run_provisioner
from app.provisioner.classifier import select_packs


def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_local()


def test_onboarding_to_provisioner_snapshot() -> None:
    db = setup_db()
    org = Org(name="Test Org", locale_default="en")
    db.add(org)
    db.commit()
    db.refresh(org)
    profile = OrgProfile(org_id=org.id, onboarding_stage=0)
    db.add(profile)
    db.commit()

    answers = {
        "industry": "dentist",
        "primary_goal": "bookings",
        "primary_channel": "whatsapp",
    }
    selection = select_packs(answers)
    profile.selected_packs_json = json.dumps(selection.pack_ids)
    profile.onboarding_stage = 1
    db.commit()

    result = run_provisioner(db, org.id, selection.pack_ids)
    snapshot = db.query(OrgConfigSnapshot).first()
    assert snapshot is not None
    assert result["status"] == "ok"


def test_rollback_restores_previous_config() -> None:
    db = setup_db()
    org = Org(name="Rollback Org", locale_default="en")
    db.add(org)
    db.commit()
    db.refresh(org)
    config = OrgConfig(org_id=org.id, active_config_json="{}")
    db.add(config)
    db.commit()

    snapshot = OrgConfigSnapshot(
        org_id=org.id,
        snapshot_id="snap-1",
        config_json=json.dumps({"layout": {"tabs": ["Runs"]}}),
        reason="test",
        pack_versions=json.dumps({"dentist-core": "1.0.0"}),
    )
    db.add(snapshot)
    db.commit()

    config.active_config_json = json.dumps({"layout": {"tabs": ["Other"]}})
    db.commit()

    config.active_config_json = snapshot.config_json
    db.commit()

    assert json.loads(config.active_config_json)["layout"]["tabs"] == ["Runs"]
