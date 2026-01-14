import asyncio
import os
import uuid
from dataclasses import dataclass
from typing import Any
import aiohttp
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

API_URL = os.getenv("API_URL", "http://api:8000")


@dataclass
class RunInput:
    run_id: str
    payload: dict[str, Any]


@activity.defn
async def update_status(run_id: str, status: str) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{API_URL}/api/runs/{run_id}/status",
            json={"status": status},
        )


@activity.defn
async def emit_step(run_id: str, step: int) -> None:
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{API_URL}/api/runs/{run_id}/status",
            json={"status": "RUNNING"},
        )


@workflow.defn
class RunWorkflow:
    @workflow.run
    async def run(self, run_input: RunInput) -> str:
        await workflow.execute_activity(update_status, run_input.run_id, "RUNNING", start_to_close_timeout=30)
        for step in range(1, 4):
            await workflow.execute_activity(emit_step, run_input.run_id, step, start_to_close_timeout=30)
            await asyncio.sleep(1)
        return "COMPLETED"


@workflow.defn
class HealWorkflow:
    @workflow.run
    async def run(self, run_id: str) -> str:
        await workflow.execute_activity(update_status, run_id, "RUNNING", start_to_close_timeout=30)
        return "HEALED"


@workflow.defn
class SessionWorkflow:
    @workflow.run
    async def run(self, run_id: str) -> str:
        await workflow.execute_activity(update_status, run_id, "RUNNING", start_to_close_timeout=30)
        return "SESSION_READY"


async def main() -> None:
    client = await Client.connect(os.getenv("TEMPORAL_ADDRESS", "temporal:7233"))
    worker = Worker(
        client,
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "agent-swarm"),
        workflows=[RunWorkflow, HealWorkflow, SessionWorkflow],
        activities=[update_status, emit_step],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
