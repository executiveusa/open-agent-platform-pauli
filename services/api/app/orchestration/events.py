import asyncio
from collections import defaultdict
from collections.abc import AsyncGenerator
from typing import Any


class EventBroker:
    def __init__(self) -> None:
        self.queues: dict[str, asyncio.Queue[dict[str, Any]]] = defaultdict(asyncio.Queue)

    async def publish(self, run_id: str, payload: dict[str, Any]) -> None:
        await self.queues[run_id].put(payload)

    async def stream(self, run_id: str) -> AsyncGenerator[dict[str, Any], None]:
        queue = self.queues[run_id]
        while True:
            payload = await queue.get()
            yield payload


broker = EventBroker()
