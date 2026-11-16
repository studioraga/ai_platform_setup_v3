
"""Offline signed JWT and identity-boundary regression."""

import base64
import json
import sys

from pathlib import Path

import pytest

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


LAB = Path(__file__).resolve().parents[2] / "labs/r07"
sys.path.insert(0, str(LAB))

from verified_identity import (
    IdentityConfig,
    IdentityDenied,
    verify_jwt,
)


PRIVATE_KEY = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

CONFIG = IdentityConfig(
    issuer="https://offline-issuer.invalid/",
    audience="principal-r07-lab",
    public_keys={"lab-kid": PRIVATE_KEY.public_key()},
    role_capabilities={
        "observer": frozenset({"measurement:read"}),
        "diagnostician": frozenset({"diagnostic:run"}),
    },
)


def b64(value):
    if isinstance(value, dict):
        value = json.dumps(
            value, sort_keys=True, separators=(",", ":")
        ).encode()
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def signed_token(claim_changes=None, header_changes=None, key=None):
    header = {"alg": "RS256", "typ": "JWT", "kid": "lab-kid"}
    claims = {
        "iss": CONFIG.issuer,
        "aud": CONFIG.audience,
        "sub": "operator-a",
        "tenant_id": "tenant_a",
        "roles": ["observer", "diagnostician"],
        "iat": 900,
        "nbf": 900,
        "exp": 2000,
    }
    header.update(header_changes or {})
    claims.update(claim_changes or {})

    body = f"{b64(header)}.{b64(claims)}"
    signer = key or PRIVATE_KEY
    signature = signer.sign(
        body.encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return f"{body}.{b64(signature)}"


def check(token, config=CONFIG):
    return verify_jwt(token, config, now=1000)


def test_valid_signed_identity():
    principal = check(signed_token())
    assert principal.subject == "operator-a"
    assert principal.tenant_id == "tenant_a"
    assert "diagnostic:run" in principal.capabilities


def test_claimed_capabilities_are_not_trusted():
    token = signed_token({
        "roles": ["observer"],
        "capabilities": ["bus:reset"],
    })
    assert check(token).capabilities == frozenset({
        "measurement:read"
    })


@pytest.mark.parametrize("claims,reason", [
    ({"iss": "https://wrong.invalid/"}, "INVALID_ISSUER"),
    ({"aud": "wrong-audience"}, "INVALID_AUDIENCE"),
    ({"exp": 999}, "TOKEN_EXPIRED"),
    ({"nbf": 1100}, "TOKEN_NOT_YET_VALID"),
    ({"sub": ""}, "SUBJECT_REQUIRED"),
    ({"tenant_id": ""}, "TENANT_REQUIRED"),
    ({"roles": ["admin-unknown"]}, "UNAUTHORIZED_ROLE"),
])
def test_bad_claims_denied(claims, reason):
    with pytest.raises(IdentityDenied, match=reason):
        check(signed_token(claims))


@pytest.mark.parametrize("header,reason", [
    ({"alg": "none"}, "ALGORITHM_NOT_ALLOWED"),
    ({"kid": "missing"}, "UNKNOWN_KEY_ID"),
    ({"jku": "https://attacker.invalid/jwks"}, "UNTRUSTED_KEY_SOURCE"),
])
def test_bad_headers_denied(header, reason):
    with pytest.raises(IdentityDenied, match=reason):
        check(signed_token(header_changes=header))


def test_tampered_signature_denied():
    parts = signed_token().split(".")
    parts[1] = b64({"sub": "attacker"})
    with pytest.raises(IdentityDenied, match="INVALID_SIGNATURE"):
        check(".".join(parts))


def test_attacker_key_denied():
    other = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    with pytest.raises(IdentityDenied, match="INVALID_SIGNATURE"):
        check(signed_token(key=other))


def test_malformed_token_denied():
    with pytest.raises(IdentityDenied, match="INVALID_TOKEN"):
        check("not-a-jwt")
