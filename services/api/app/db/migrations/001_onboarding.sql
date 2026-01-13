CREATE TABLE orgs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  locale_default VARCHAR(16) NOT NULL DEFAULT 'en',
  branding_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE users ADD COLUMN org_id INTEGER REFERENCES orgs(id);

CREATE TABLE onboarding_sessions (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  user_id INTEGER REFERENCES users(id),
  status VARCHAR(64) NOT NULL DEFAULT 'active',
  locale VARCHAR(16) NOT NULL DEFAULT 'en',
  persona_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP
);

CREATE TABLE onboarding_answers (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES onboarding_sessions(id),
  question_id VARCHAR(128) NOT NULL,
  answer_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE org_profile (
  org_id INTEGER PRIMARY KEY REFERENCES orgs(id),
  profile_json TEXT,
  onboarding_stage INTEGER NOT NULL DEFAULT 0,
  selected_packs_json TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendations (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  rec_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE org_configs (
  org_id INTEGER PRIMARY KEY REFERENCES orgs(id),
  active_config_json TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE org_config_snapshots (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  snapshot_id VARCHAR(128) NOT NULL,
  config_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  reason VARCHAR(128) NOT NULL,
  pack_versions TEXT
);
