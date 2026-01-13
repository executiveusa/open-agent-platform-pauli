import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ..core.security import ApiKeyDep
from ..core.rate_limit import rate_limiter
from ..orchestration.events import broker


router = APIRouter(prefix="/api/setup", tags=["setup"], dependencies=[ApiKeyDep])


@router.get("/events")
async def setup_events(request: Request) -> StreamingResponse:
    rate_limiter.check(request)
    org_id = 1

    async def event_generator():
        yield "event: status\ndata: CONNECTED\n\n"
        async for payload in broker.stream(f"setup-{org_id}"):
            event_type = payload.get("type", "message")
            data = payload.get("data") if "data" in payload else payload
            if event_type == "status" and isinstance(data, str):
                yield f"event: status\ndata: {data}\n\n"
            else:
                yield f"event: {event_type}\n"
                yield f"data: {json.dumps(data)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
