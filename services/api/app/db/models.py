import enum
from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class RunStatus(str, enum.Enum):
    queued = "QUEUED"
    running = "RUNNING"
    waiting_tool = "WAITING_TOOL"
    needs_approval = "NEEDS_APPROVAL"
    failed = "FAILED"
    completed = "COMPLETED"
    canceled = "CANCELED"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Org(Base):
    __tablename__ = "orgs"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    locale_default = Column(String(16), nullable=False, default="en")
    branding_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OnboardingSession(Base):
    __tablename__ = "onboarding_sessions"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(64), nullable=False, default="active")
    locale = Column(String(16), nullable=False, default="en")
    persona_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class OnboardingAnswer(Base):
    __tablename__ = "onboarding_answers"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("onboarding_sessions.id"), nullable=False)
    question_id = Column(String(128), nullable=False)
    answer_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrgProfile(Base):
    __tablename__ = "org_profile"

    org_id = Column(Integer, ForeignKey("orgs.id"), primary_key=True)
    profile_json = Column(Text, nullable=True)
    onboarding_stage = Column(Integer, default=0, nullable=False)
    selected_packs_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrgSettings(Base):
    __tablename__ = "org_settings"

    org_id = Column(Integer, ForeignKey("orgs.id"), primary_key=True)
    autonomy_mode = Column(String(32), nullable=False, default="tiered")
    fuck_it_expires_at = Column(DateTime, nullable=True)
    policy_overrides = Column(Text, nullable=True)
    branding_json = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    actor = Column(String(128), nullable=False)
    action = Column(String(128), nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    rec_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketplacePack(Base):
    __tablename__ = "marketplace_packs"

    id = Column(Integer, primary_key=True)
    pack_id = Column(String(128), nullable=False)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrgPackInstall(Base):
    __tablename__ = "org_pack_installs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    pack_id = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="enabled")
    installed_at = Column(DateTime, default=datetime.utcnow)


class OrgConfig(Base):
    __tablename__ = "org_configs"

    org_id = Column(Integer, ForeignKey("orgs.id"), primary_key=True)
    active_config_json = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrgConfigSnapshot(Base):
    __tablename__ = "org_config_snapshots"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    snapshot_id = Column(String(128), nullable=False)
    config_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reason = Column(String(128), nullable=False)
    pack_versions = Column(Text, nullable=True)
    config_checksum = Column(String(64), nullable=True)


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    event_type = Column(String(64), nullable=False)
    pack_ids = Column(Text, nullable=True)
    payload_json = Column(Text, nullable=True)
    privacy_json = Column(Text, nullable=True)
    schema_version = Column(String(16), nullable=False, default="1")
    created_at = Column(DateTime, default=datetime.utcnow)


class PackMetricsDaily(Base):
    __tablename__ = "pack_metrics_daily"

    id = Column(Integer, primary_key=True)
    pack_id = Column(String(128), nullable=False)
    metrics_json = Column(Text, nullable=False)
    metric_date = Column(DateTime, default=datetime.utcnow)


class OrgMetricsDaily(Base):
    __tablename__ = "org_metrics_daily"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    metrics_json = Column(Text, nullable=False)
    metric_date = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    config_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id = Column(Integer, primary_key=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("orgs.id"), nullable=False)
    assignment = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String(64), unique=True, nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    status = Column(Enum(RunStatus), default=RunStatus.queued, nullable=False)
    trace_id = Column(String(128), nullable=True)
    model_used = Column(String(128), nullable=True)
    inputs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    steps = relationship("RunStep", back_populates="run")
    artifacts = relationship("Artifact", back_populates="run")
    failures = relationship("Failure", back_populates="run")


class RunStep(Base):
    __tablename__ = "run_steps"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    status = Column(String(64), nullable=False)
    tool = Column(String(128), nullable=True)
    inputs = Column(Text, nullable=True)
    outputs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="steps")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="artifacts")


class Failure(Base):
    __tablename__ = "failures"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    error = Column(Text, nullable=False)
    stack = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)
    screenshot_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("Run", back_populates="failures")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    novnc_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
