"""Shared fixtures for SCM MCP integration tests."""
import os
import sys
import pytest
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from src.client import get_client  # noqa: E402
from src.utils import serialize    # noqa: E402

TEST_FOLDER = "PACNW"
PREFIX = "pytest-mcp-"


def _get_or_create(resource, create_payload, folder=None):
    """Create an object, or find and return it if it already exists by name."""
    name = create_payload["name"]
    try:
        obj = resource.create(create_payload)
        return obj, True
    except Exception as exc:
        if "already exists" in str(exc) or "OBJECT_ALREADY_EXISTS" in str(exc) or "NameNotUnique" in type(exc).__name__:
            items = resource.list(folder=folder) if folder else resource.list()
            for item in items:
                if getattr(item, "name", None) == name:
                    return item, False
        raise


@pytest.fixture(scope="session")
def client():
    return get_client()


@pytest.fixture(scope="session")
def state():
    """Session-wide dict for passing created IDs between dependent tests."""
    return {}


@pytest.fixture(scope="session")
def test_zone(client):
    """Create a zone used by security/decryption/auth/NAT/PBF/QoS rule tests."""
    name = f"{PREFIX}zone"
    obj, created = _get_or_create(
        client.security_zone,
        {"name": name, "folder": TEST_FOLDER},
        folder=TEST_FOLDER,
    )
    yield {"name": name, "id": str(obj.id)}
    if created:
        try:
            client.security_zone.delete(obj.id)
        except Exception:
            pass


@pytest.fixture(scope="session")
def test_address(client):
    """Create a reusable address object for group/rule tests."""
    name = f"{PREFIX}dep-addr"
    obj, created = _get_or_create(
        client.address,
        {"name": name, "folder": TEST_FOLDER, "ip_netmask": "203.0.113.1/32"},
        folder=TEST_FOLDER,
    )
    yield {"name": name, "id": str(obj.id)}
    if created:
        try:
            client.address.delete(obj.id)
        except Exception:
            pass


@pytest.fixture(scope="session")
def test_service(client):
    """Create a reusable service object for service-group tests."""
    name = f"{PREFIX}dep-svc"
    obj, created = _get_or_create(
        client.service,
        {"name": name, "folder": TEST_FOLDER, "protocol": {"tcp": {"port": "9999"}}},
        folder=TEST_FOLDER,
    )
    yield {"name": name, "id": str(obj.id)}
    if created:
        try:
            client.service.delete(obj.id)
        except Exception:
            pass
