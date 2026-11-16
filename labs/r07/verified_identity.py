
"""R07/R11 offline JWT identity verification research.

Only RS256 tokens are supported. Public keys must come from a
trusted application configuration, never from token headers.

This is not a complete OIDC provider/JWKS lifecycle integration.
"""

import base64
import binascii
import json
import math
import time

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes

from governed_runtime import Principal


class IdentityDenied(Exception):
    """JWT verification or trusted identity mapping failed."""


@dataclass(frozen=True)
class IdentityConfig:
    issuer: str
    audience: str
    public_keys: dict[str, rsa.RSAPublicKey]
    role_capabilities: dict[str, frozenset[str]]
    leeway_seconds: int = 0


def _decode(segment: str) -> bytes:
    if not segment or len(segment) > 65536:
        raise IdentityDenied("INVALID_TOKEN_ENCODING")
    try:
        return base64.b64decode(
            segment + "=" * (-len(segment) % 4),
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, binascii.Error) as exc:
        raise IdentityDenied("INVALID_TOKEN_ENCODING") from exc


def _unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise IdentityDenied("DUPLICATE_JSON_FIELD")
        out[key] = value
    return out


def _read_json(segment: str) -> dict:
    try:
        value = json.loads(
            _decode(segment),
            object_pairs_hook=_unique_pairs,
        )
    except (UnicodeError, ValueError, TypeError) as exc:
        raise IdentityDenied("INVALID_TOKEN_JSON") from exc
    if not isinstance(value, dict):
        raise IdentityDenied("INVALID_TOKEN_JSON")
    return value


def _timestamp(value, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise IdentityDenied(f"INVALID_{label}")
    return float(value)


def verify_jwt(
    token: str,
    config: IdentityConfig,
    *,
    now: float | None = None,
) -> Principal:
    """Validate signed claims before constructing an R07 Principal."""
    if not isinstance(token, str) or len(token) > 16384:
        raise IdentityDenied("INVALID_TOKEN")

    segments = token.split(".")
    if len(segments) != 3:
        raise IdentityDenied("INVALID_TOKEN")

    header = _read_json(segments[0])

    if header.get("alg") != "RS256":
        raise IdentityDenied("ALGORITHM_NOT_ALLOWED")
    if header.get("typ") not in ("JWT", "at+jwt"):
        raise IdentityDenied("INVALID_TOKEN_TYPE")
    if any(k in header for k in ("jku", "jwk", "x5u", "crit")):
        raise IdentityDenied("UNTRUSTED_KEY_SOURCE")

    kid = header.get("kid")
    if not isinstance(kid, str) or not kid:
        raise IdentityDenied("MISSING_KEY_ID")

    key = config.public_keys.get(kid)
    if not isinstance(key, rsa.RSAPublicKey):
        raise IdentityDenied("UNKNOWN_KEY_ID")

    signing_input = ".".join(segments[:2]).encode("ascii")
    signature = _decode(segments[2])

    try:
        key.verify(
            signature,
            signing_input,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
    except (InvalidSignature, ValueError) as exc:
        raise IdentityDenied("INVALID_SIGNATURE") from exc

    claims = _read_json(segments[1])
    current = time.time() if now is None else float(now)

    if claims.get("iss") != config.issuer:
        raise IdentityDenied("INVALID_ISSUER")

    audience = claims.get("aud")
    aud_valid = (
        audience == config.audience
        if isinstance(audience, str)
        else isinstance(audience, list)
        and all(isinstance(x, str) for x in audience)
        and config.audience in audience
    )
    if not aud_valid:
        raise IdentityDenied("INVALID_AUDIENCE")

    leeway = config.leeway_seconds
    if not isinstance(leeway, int) or not 0 <= leeway <= 60:
        raise IdentityDenied("INVALID_LEEWAY")

    exp = _timestamp(claims.get("exp"), "EXPIRY")
    if current >= exp + leeway:
        raise IdentityDenied("TOKEN_EXPIRED")

    if "nbf" in claims:
        if current + leeway < _timestamp(claims["nbf"], "NOT_BEFORE"):
            raise IdentityDenied("TOKEN_NOT_YET_VALID")

    if "iat" in claims:
        if current + leeway < _timestamp(claims["iat"], "ISSUED_AT"):
            raise IdentityDenied("TOKEN_ISSUED_IN_FUTURE")

    subject = claims.get("sub")
    tenant_id = claims.get("tenant_id")
    roles = claims.get("roles")

    if not isinstance(subject, str) or not subject.strip():
        raise IdentityDenied("SUBJECT_REQUIRED")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise IdentityDenied("TENANT_REQUIRED")
    if not isinstance(roles, list) or not roles:
        raise IdentityDenied("ROLES_REQUIRED")
    if not all(isinstance(r, str) for r in roles):
        raise IdentityDenied("INVALID_ROLES")

    # Capabilities are assigned by trusted application policy,
    # never by accepting a 'capabilities' claim from the JWT.
    capabilities = set()
    for role in roles:
        if role not in config.role_capabilities:
            raise IdentityDenied("UNAUTHORIZED_ROLE")
        capabilities.update(config.role_capabilities[role])

    return Principal(
        subject=subject,
        tenant_id=tenant_id,
        capabilities=frozenset(capabilities),
    )
