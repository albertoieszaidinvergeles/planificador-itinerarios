import os
from typing import Any

import jwt
from jwt import PyJWKClient


class AuthenticationError(Exception):
    """A session token is missing or cannot be verified."""


def verify_session_token(token: str) -> dict[str, Any]:
    issuer = os.getenv("CLERK_ISSUER", "").strip()
    if not issuer:
        raise AuthenticationError("Clerk issuer is not configured.")

    audience = os.getenv("CLERK_AUDIENCE", "").strip() or None
    jwks_url = issuer.rstrip("/") + "/.well-known/jwks.json"

    try:
        signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience,
            options={
                "require": ["iss", "exp"],
                "verify_aud": audience is not None,
            },
        )
    except (jwt.PyJWTError, ValueError, TypeError, KeyError) as error:
        raise AuthenticationError("Invalid Clerk session token.") from error


def bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise AuthenticationError("Missing bearer token.")

    scheme, separator, credentials = authorization.partition(" ")
    if (
        not separator
        or scheme.lower() != "bearer"
        or not credentials
        or credentials.strip() != credentials
        or " " in credentials
    ):
        raise AuthenticationError("Invalid bearer token.")

    return credentials


def verify_bearer_token(authorization: str | None) -> dict[str, Any]:
    return verify_session_token(bearer_token(authorization))
