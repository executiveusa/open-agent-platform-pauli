import hmac
import hashlib
from .config import get_settings


def sign_token(token: str) -> str:
    secret = get_settings().run_token_secret.encode()
    signature = hmac.new(secret, token.encode(), hashlib.sha256).hexdigest()
    return f"{token}.{signature}"
