"""SCM client factory — initialized from environment variables, cached per TSG."""

import os

from dotenv import load_dotenv
from scm.client import Scm

load_dotenv()

_clients: dict[str, Scm] = {}


def _resolve_tsg(tsg_id: str | None) -> str:
    """Resolve a tsg_id argument to a concrete TSG ID string.

    Accepts:
    - None → use SCM_TSG_ID env var (default)
    - Named alias like "PROD" → look up SCM_TSG_PROD env var, fall back to raw value
    - Raw numeric ID → use as-is
    """
    if tsg_id is None:
        return os.environ.get("SCM_TSG_ID", "")
    alias_val = os.environ.get(f"SCM_TSG_{tsg_id.upper()}")
    return alias_val if alias_val else tsg_id


def _resolve_credentials(alias: str | None) -> tuple[str | None, str | None]:
    """Return (client_id, client_secret) for the given alias, falling back to global defaults.

    Per-TSG credentials use SCM_TSG_<ALIAS>_CLIENT_ID / SCM_TSG_<ALIAS>_CLIENT_SECRET.
    """
    if alias:
        key = alias.upper()
        per_id = os.environ.get(f"SCM_TSG_{key}_CLIENT_ID")
        per_secret = os.environ.get(f"SCM_TSG_{key}_CLIENT_SECRET")
        if per_id and per_secret:
            return per_id, per_secret
    return os.environ.get("SCM_CLIENT_ID"), os.environ.get("SCM_CLIENT_SECRET")


def get_client(tsg_id: str | None = None) -> Scm:
    """Return a cached SCM client for the given TSG, validating credentials at first use."""
    resolved = _resolve_tsg(tsg_id)
    if resolved in _clients:
        return _clients[resolved]

    alias = tsg_id.upper() if tsg_id else None
    client_id, client_secret = _resolve_credentials(alias)

    missing = [k for k, v in {
        "SCM_CLIENT_ID": client_id,
        "SCM_CLIENT_SECRET": client_secret,
        "SCM_TSG_ID (or named alias)": resolved or None,
    }.items() if not v]

    if missing:
        raise RuntimeError(
            f"Missing required SCM credentials: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your SCM credentials."
        )

    client = Scm(
        client_id=client_id,
        client_secret=client_secret,
        tsg_id=resolved,
    )
    _clients[resolved] = client
    return client


def list_tsg_profiles() -> list[dict]:
    """Return configured TSG profiles (names only, no credential values)."""
    profiles = []
    default_tsg = os.environ.get("SCM_TSG_ID")
    if default_tsg:
        profiles.append({"name": "default", "alias": "SCM_TSG_ID"})
    for key, val in os.environ.items():
        if key.startswith("SCM_TSG_") and key != "SCM_TSG_ID" and val:
            alias_name = key[len("SCM_TSG_"):]
            profiles.append({"name": alias_name.lower(), "alias": key})
    return profiles
