CREATE TABLE org_settings (
  org_id INTEGER PRIMARY KEY REFERENCES orgs(id),
  autonomy_mode VARCHAR(32) NOT NULL DEFAULT "tiered",
  fuck_it_expires_at TIMESTAMP,
  policy_overrides TEXT,
  branding_json TEXT,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  actor VARCHAR(128) NOT NULL,
  action VARCHAR(128) NOT NULL,
  details_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE marketplace_packs (
  id SERIAL PRIMARY KEY,
  pack_id VARCHAR(128) NOT NULL,
  metadata_json TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE org_pack_installs (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  pack_id VARCHAR(128) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT "enabled",
  installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE telemetry_events (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  event_type VARCHAR(64) NOT NULL,
  pack_ids TEXT,
  payload_json TEXT,
  privacy_json TEXT,
  schema_version VARCHAR(16) NOT NULL DEFAULT "1",
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pack_metrics_daily (
  id SERIAL PRIMARY KEY,
  pack_id VARCHAR(128) NOT NULL,
  metrics_json TEXT NOT NULL,
  metric_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE org_metrics_daily (
  id SERIAL PRIMARY KEY,
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  metrics_json TEXT NOT NULL,
  metric_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  config_json TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE experiment_assignments (
  id SERIAL PRIMARY KEY,
  experiment_id INTEGER NOT NULL REFERENCES experiments(id),
  org_id INTEGER NOT NULL REFERENCES orgs(id),
  assignment VARCHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
