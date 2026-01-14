# Architecture

## Overview
Dashboard Agent Swarm vNext extends the Open Agent Platform with a FastAPI backend, Temporal workflows, and a containerized automation runner. The platform separates the UI (Next.js) from orchestration (FastAPI), and executes each agent run in durable workflows backed by Postgres + Temporal.

## Services
- **apps/web**: Next.js 15.3 UI dashboard.
- **services/api**: FastAPI orchestration layer, SSE events, run lifecycle APIs.
- **services/worker**: Temporal worker for run/heal/session workflows.
- **services/runner**: Playwright + VNC/noVNC runner image for live desktop sessions.
- **infra/docker/docker-compose.yml**: Self-host stack for VPS/Coolify.

## Data model
Postgres tables:
- users
- agents
- runs
- run_steps
- artifacts
- failures
- sessions

## Durability + retries
Temporal handles long-running workflows and retries. The worker ships `RunWorkflow`, `HealWorkflow`, and `SessionWorkflow` to orchestrate run steps and recovery.

## Realtime visibility
SSE (`/api/runs/{id}/events`) streams status, steps, logs, and session URLs to the dashboard.

## Security
- API key header for server-only calls.
- Signed session tokens for noVNC access.
- Rate limits on public endpoints.

## Future adapters
LangGraph is default. crewAI + AutoGen adapters are stubbed for later.
