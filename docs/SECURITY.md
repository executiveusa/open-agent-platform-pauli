# Security

## Secrets
All secrets are server-side only. The frontend never stores API keys or model credentials.

## Authentication
The API enforces an optional API key via `X-API-Key` header.

## Rate limiting
Requests are rate limited per IP.

## Desktop sessions
noVNC URLs are issued via signed tokens with short expiry. Sessions are not publicly exposed without auth.
