# Product Requirements Document

## Vision
Deliver a self-hostable agent platform with a friendly dashboard, live run monitoring, and durable automation.

## Personas
- Operations lead launching repeatable agent tasks.
- Developer managing agent packs and orchestration.

## Goals
1. Run long-lived agent jobs in containers.
2. Watch runs live with logs, steps, artifacts, and desktop sessions.
3. Provide recovery workflows for failures.
4. Self-hostable on a single VPS.

## MVP
- Runs list + run detail dashboard.
- FastAPI run APIs with SSE events.
- Temporal workflows for durability.
- Playwright runner with noVNC.

## Non-goals
- Any content piracy workflow.
