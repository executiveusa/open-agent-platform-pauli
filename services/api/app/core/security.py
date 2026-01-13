from fastapi import Depends, Header, HTTPException, status
from .config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.api_token is None:
        return
    if x_api_key != settings.api_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


ApiKeyDep = Depends(require_api_key)
