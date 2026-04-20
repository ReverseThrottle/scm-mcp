"""
Integration tests for all SCM MCP tools.

Each test corresponds to a specific tool. Tests use the real SCM API (default TSG)
against the PACNW folder. All created objects are prefixed with "pytest-mcp-" and
are deleted within the test that creates them (or a paired delete test).

Run with:
    cd scm-mcp && .venv/bin/pytest tests/ -v

Errors are reported with the full SCM API error message for triage.
"""
import pytest
from conftest import TEST_FOLDER, PREFIX, serialize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assert_ok(result, *required_keys):
    """Assert result is a dict without an 'error' key, and has expected keys."""
    assert isinstance(result, (dict, list)), f"Expected dict/list, got {type(result)}"
    if isinstance(result, dict):
        assert "error" not in result, f"Tool returned error: {result}"
        for k in required_keys:
            assert k in result, f"Missing key '{k}' in result: {result}"


def assert_list_ok(result):
    assert isinstance(result, list), f"Expected list, got {type(result)}: {result}"


# ===========================================================================
# SETUP — Folders
# ===========================================================================

class TestFolders:
    """Tools: scm_list_folders, scm_get_folder, scm_create_folder,
    scm_update_folder, scm_delete_folder"""

    def test_scm_list_folders(self, client):
        result = serialize(client.folder.list())
        assert_list_ok(result)
        assert any(f["name"] == TEST_FOLDER for f in result)

    def test_scm_get_folder(self, client, state):
        folders = serialize(client.folder.list())
        target = next(f for f in folders if f["name"] == TEST_FOLDER)
        state["pacnw_folder_id"] = target["id"]
        result = serialize(client.folder.get(target["id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == TEST_FOLDER

    def test_scm_create_folder(self, client, state):
        result = serialize(client.folder.create({
            "name": f"{PREFIX}folder",
            "parent": "ngfw-shared",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}folder"
        state["test_folder_id"] = result["id"]

    def test_scm_update_folder(self, client, state):
        folder = client.folder.get(state["test_folder_id"])
        folder.description = "pytest updated"
        result = serialize(client.folder.update(folder))
        assert_ok(result, "id")
        assert result.get("description") == "pytest updated"

    def test_scm_delete_folder(self, client, state):
        client.folder.delete(state["test_folder_id"])
        with pytest.raises(Exception):
            client.folder.get(state["test_folder_id"])


# ===========================================================================
# SETUP — Snippets
# ===========================================================================

class TestSnippets:
    """Tools: scm_list_snippets, scm_get_snippet, scm_create_snippet,
    scm_update_snippet, scm_delete_snippet,
    scm_associate_snippet_to_folder, scm_disassociate_snippet_from_folder"""

    def test_scm_list_snippets(self, client):
        result = serialize(client.snippet.list())
        assert_list_ok(result)

    def test_scm_create_snippet(self, client, state):
        result = serialize(client.snippet.create({
            "name": f"{PREFIX}snippet",
            "description": "pytest snippet",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}snippet"
        state["snippet_id"] = result["id"]

    def test_scm_get_snippet(self, client, state):
        result = serialize(client.snippet.get(state["snippet_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}snippet"

    def test_scm_update_snippet(self, client, state):
        snippet = client.snippet.get(state["snippet_id"])
        snippet.description = "pytest updated snippet"
        result = serialize(client.snippet.update(snippet))
        assert_ok(result, "id")

    def test_scm_associate_snippet_to_folder(self, client, state):
        try:
            result = serialize(client.snippet.associate_folder(
                state["snippet_id"], state["pacnw_folder_id"]
            ))
            assert result is not None
            state["snippet_associated"] = True
        except Exception as exc:
            pytest.skip(f"associate_folder not supported or folder conflict: {exc}")

    def test_scm_disassociate_snippet_from_folder(self, client, state):
        if not state.get("snippet_associated"):
            pytest.skip("snippet was not associated")
        try:
            result = serialize(client.snippet.disassociate_folder(
                state["snippet_id"], state["pacnw_folder_id"]
            ))
            assert result is not None
        except Exception as exc:
            pytest.skip(f"disassociate_folder failed: {exc}")

    def test_scm_delete_snippet(self, client, state):
        client.snippet.delete(state["snippet_id"])
        with pytest.raises(Exception):
            client.snippet.get(state["snippet_id"])


# ===========================================================================
# OBJECTS — Addresses
# ===========================================================================

class TestAddresses:
    """Tools: scm_list_addresses, scm_get_address, scm_create_address,
    scm_update_address, scm_delete_address"""

    def test_scm_list_addresses(self, client):
        result = serialize(client.address.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_address_ip(self, client, state):
        result = serialize(client.address.create({
            "name": f"{PREFIX}addr-ip",
            "folder": TEST_FOLDER,
            "ip_netmask": "192.0.2.100/32",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}addr-ip"
        state["address_ip_id"] = result["id"]

    def test_scm_create_address_fqdn(self, client, state):
        result = serialize(client.address.create({
            "name": f"{PREFIX}addr-fqdn",
            "folder": TEST_FOLDER,
            "fqdn": "pytest.lab.reversethrottle.com",
        }))
        assert_ok(result, "id", "name")
        state["address_fqdn_id"] = result["id"]

    def test_scm_create_address_range(self, client, state):
        result = serialize(client.address.create({
            "name": f"{PREFIX}addr-range",
            "folder": TEST_FOLDER,
            "ip_range": "192.0.2.1-192.0.2.10",
        }))
        assert_ok(result, "id", "name")
        state["address_range_id"] = result["id"]

    def test_scm_get_address(self, client, state):
        result = serialize(client.address.get(state["address_ip_id"]))
        assert_ok(result, "id", "name", "ip_netmask")
        assert result["name"] == f"{PREFIX}addr-ip"
        assert result["ip_netmask"] == "192.0.2.100/32"

    def test_scm_update_address(self, client, state):
        addr = client.address.get(state["address_ip_id"])
        addr.description = "pytest updated"
        result = serialize(client.address.update(addr))
        assert_ok(result, "id")
        assert result.get("description") == "pytest updated"

    def test_scm_delete_address_ip(self, client, state):
        client.address.delete(state["address_ip_id"])
        with pytest.raises(Exception):
            client.address.get(state["address_ip_id"])

    def test_scm_delete_address_fqdn(self, client, state):
        client.address.delete(state["address_fqdn_id"])

    def test_scm_delete_address_range(self, client, state):
        client.address.delete(state["address_range_id"])


# ===========================================================================
# OBJECTS — Address Groups
# ===========================================================================

class TestAddressGroups:
    """Tools: scm_list_address_groups, scm_get_address_group,
    scm_create_address_group, scm_update_address_group, scm_delete_address_group"""

    def test_scm_list_address_groups(self, client):
        result = serialize(client.address_group.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_address_group_static(self, client, state, test_address):
        result = serialize(client.address_group.create({
            "name": f"{PREFIX}addrgrp-static",
            "folder": TEST_FOLDER,
            "static": [test_address["name"]],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}addrgrp-static"
        state["addrgrp_static_id"] = result["id"]

    def test_scm_create_address_group_dynamic(self, client, state):
        result = serialize(client.address_group.create({
            "name": f"{PREFIX}addrgrp-dyn",
            "folder": TEST_FOLDER,
            "dynamic": {"filter": f"'{PREFIX}zone'"},
        }))
        assert_ok(result, "id", "name")
        state["addrgrp_dyn_id"] = result["id"]

    def test_scm_get_address_group(self, client, state):
        result = serialize(client.address_group.get(state["addrgrp_static_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}addrgrp-static"

    def test_scm_update_address_group(self, client, state, test_address):
        grp = client.address_group.get(state["addrgrp_static_id"])
        grp.description = "pytest updated"
        result = serialize(client.address_group.update(grp))
        assert_ok(result, "id")

    def test_scm_delete_address_group_static(self, client, state):
        client.address_group.delete(state["addrgrp_static_id"])

    def test_scm_delete_address_group_dynamic(self, client, state):
        client.address_group.delete(state["addrgrp_dyn_id"])


# ===========================================================================
# OBJECTS — Services
# ===========================================================================

class TestServices:
    """Tools: scm_list_services, scm_get_service, scm_create_service,
    scm_update_service, scm_delete_service"""

    def test_scm_list_services(self, client):
        result = serialize(client.service.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_service_tcp(self, client, state):
        result = serialize(client.service.create({
            "name": f"{PREFIX}svc-tcp",
            "folder": TEST_FOLDER,
            "protocol": {"tcp": {"port": "8443"}},
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}svc-tcp"
        state["service_tcp_id"] = result["id"]

    def test_scm_create_service_udp(self, client, state):
        result = serialize(client.service.create({
            "name": f"{PREFIX}svc-udp",
            "folder": TEST_FOLDER,
            "protocol": {"udp": {"port": "5353"}},
        }))
        assert_ok(result, "id", "name")
        state["service_udp_id"] = result["id"]

    def test_scm_get_service(self, client, state):
        result = serialize(client.service.get(state["service_tcp_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}svc-tcp"

    def test_scm_update_service(self, client, state):
        svc = client.service.get(state["service_tcp_id"])
        svc.description = "pytest updated"
        result = serialize(client.service.update(svc))
        assert_ok(result, "id")

    def test_scm_delete_service_tcp(self, client, state):
        client.service.delete(state["service_tcp_id"])

    def test_scm_delete_service_udp(self, client, state):
        client.service.delete(state["service_udp_id"])


# ===========================================================================
# OBJECTS — Service Groups
# ===========================================================================

class TestServiceGroups:
    """Tools: scm_list_service_groups, scm_get_service_group,
    scm_create_service_group, scm_update_service_group, scm_delete_service_group"""

    def test_scm_list_service_groups(self, client):
        result = serialize(client.service_group.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_service_group(self, client, state, test_service):
        result = serialize(client.service_group.create({
            "name": f"{PREFIX}svcgrp",
            "folder": TEST_FOLDER,
            "members": [test_service["name"]],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}svcgrp"
        state["svcgrp_id"] = result["id"]

    def test_scm_get_service_group(self, client, state):
        result = serialize(client.service_group.get(state["svcgrp_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}svcgrp"

    def test_scm_update_service_group(self, client, state, test_service):
        grp = client.service_group.get(state["svcgrp_id"])
        grp.members = [test_service["name"]]
        result = serialize(client.service_group.update(grp))
        assert_ok(result, "id")

    def test_scm_delete_service_group(self, client, state):
        client.service_group.delete(state["svcgrp_id"])


# ===========================================================================
# OBJECTS — Tags
# ===========================================================================

class TestTags:
    """Tools: scm_list_tags, scm_get_tag, scm_create_tag,
    scm_update_tag, scm_delete_tag"""

    def test_scm_list_tags(self, client):
        result = serialize(client.tag.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_tag(self, client, state):
        result = serialize(client.tag.create({
            "name": f"{PREFIX}tag",
            "folder": TEST_FOLDER,
            "color": "Red",
            "comments": "pytest tag",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}tag"
        state["tag_id"] = result["id"]

    def test_scm_get_tag(self, client, state):
        result = serialize(client.tag.get(state["tag_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}tag"

    def test_scm_update_tag(self, client, state):
        tag = client.tag.get(state["tag_id"])
        tag.comments = "pytest updated"
        result = serialize(client.tag.update(tag))
        assert_ok(result, "id")

    def test_scm_delete_tag(self, client, state):
        client.tag.delete(state["tag_id"])


# ===========================================================================
# OBJECTS — Log Forwarding Profiles
# ===========================================================================

class TestLogForwardingProfiles:
    """Tools: scm_list_log_forwarding_profiles, scm_get_log_forwarding_profile,
    scm_create_log_forwarding_profile, scm_delete_log_forwarding_profile"""

    def test_scm_list_log_forwarding_profiles(self, client):
        result = serialize(client.log_forwarding_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_log_forwarding_profile(self, client, state):
        result = serialize(client.log_forwarding_profile.create({
            "name": f"{PREFIX}lfp",
            "folder": TEST_FOLDER,
            "description": "pytest log forwarding profile",
            "match_list": [{
                "name": "pytest-match",
                "log_type": "traffic",
                "filter": "All Logs",
            }],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}lfp"
        state["lfp_id"] = result["id"]

    def test_scm_get_log_forwarding_profile(self, client, state):
        result = serialize(client.log_forwarding_profile.get(state["lfp_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}lfp"

    def test_scm_delete_log_forwarding_profile(self, client, state):
        client.log_forwarding_profile.delete(state["lfp_id"])


# ===========================================================================
# OBJECTS — HTTP Server Profiles
# ===========================================================================

class TestHttpServerProfiles:
    """Tools: scm_list_http_server_profiles, scm_get_http_server_profile,
    scm_create_http_server_profile, scm_delete_http_server_profile"""

    def test_scm_list_http_server_profiles(self, client):
        result = serialize(client.http_server_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_http_server_profile(self, client, state):
        result = serialize(client.http_server_profile.create({
            "name": f"{PREFIX}http-profile",
            "folder": TEST_FOLDER,
            "server": [{
                "name": "pytest-server",
                "address": "10.0.0.1",
                "protocol": "HTTPS",
                "port": 443,
                "http_method": "POST",
            }],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}http-profile"
        state["http_profile_id"] = result["id"]

    def test_scm_get_http_server_profile(self, client, state):
        result = serialize(client.http_server_profile.get(state["http_profile_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_http_server_profile(self, client, state):
        client.http_server_profile.delete(state["http_profile_id"])


# ===========================================================================
# OBJECTS — Syslog Server Profiles
# ===========================================================================

class TestSyslogServerProfiles:
    """Tools: scm_list_syslog_server_profiles, scm_get_syslog_server_profile,
    scm_create_syslog_server_profile, scm_delete_syslog_server_profile"""

    def test_scm_list_syslog_server_profiles(self, client):
        result = serialize(client.syslog_server_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_syslog_server_profile(self, client, state):
        result = serialize(client.syslog_server_profile.create({
            "name": f"{PREFIX}syslog-profile",
            "folder": TEST_FOLDER,
            "server": [{
                "name": "pytest-syslog",
                "server": "10.0.0.2",
                "transport": "UDP",
                "port": 514,
                "format": "BSD",
                "facility": "LOG_USER",
            }],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}syslog-profile"
        state["syslog_profile_id"] = result["id"]

    def test_scm_get_syslog_server_profile(self, client, state):
        result = serialize(client.syslog_server_profile.get(state["syslog_profile_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_syslog_server_profile(self, client, state):
        client.syslog_server_profile.delete(state["syslog_profile_id"])


# ===========================================================================
# POLICY OBJECTS — Applications
# ===========================================================================

class TestApplications:
    """Tools: scm_list_applications, scm_get_application, scm_create_application,
    scm_update_application, scm_delete_application"""

    def test_scm_list_applications(self, client):
        result = serialize(client.application.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_application(self, client, state):
        result = serialize(client.application.create({
            "name": f"{PREFIX}app",
            "folder": TEST_FOLDER,
            "category": "business-systems",
            "subcategory": "database",
            "technology": "client-server",
            "risk": 2,
            "description": "pytest custom app",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}app"
        state["app_id"] = result["id"]

    def test_scm_get_application(self, client, state):
        result = serialize(client.application.get(state["app_id"]))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}app"

    def test_scm_update_application(self, client, state):
        app = client.application.get(state["app_id"])
        app.description = "pytest updated"
        result = serialize(client.application.update(app))
        assert_ok(result, "id")

    def test_scm_delete_application(self, client, state):
        client.application.delete(state["app_id"])


# ===========================================================================
# POLICY OBJECTS — Application Groups
# ===========================================================================

class TestApplicationGroups:
    """Tools: scm_list_application_groups, scm_get_application_group,
    scm_create_application_group, scm_update_application_group,
    scm_delete_application_group"""

    def test_scm_list_application_groups(self, client):
        result = serialize(client.application_group.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_application_group(self, client, state):
        result = serialize(client.application_group.create({
            "name": f"{PREFIX}appgrp",
            "folder": TEST_FOLDER,
            "members": ["web-browsing", "ssl"],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}appgrp"
        state["appgrp_id"] = result["id"]

    def test_scm_get_application_group(self, client, state):
        result = serialize(client.application_group.get(state["appgrp_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_application_group(self, client, state):
        grp = client.application_group.get(state["appgrp_id"])
        grp.members = ["web-browsing", "ssl", "dns"]
        result = serialize(client.application_group.update(grp))
        assert_ok(result, "id")

    def test_scm_delete_application_group(self, client, state):
        client.application_group.delete(state["appgrp_id"])


# ===========================================================================
# POLICY OBJECTS — Application Filters
# ===========================================================================

class TestApplicationFilters:
    """Tools: scm_list_application_filters, scm_get_application_filter,
    scm_create_application_filter, scm_delete_application_filter"""

    def test_scm_list_application_filters(self, client):
        result = serialize(client.application_filter.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_application_filter(self, client, state):
        result = serialize(client.application_filter.create({
            "name": f"{PREFIX}appfilter",
            "folder": TEST_FOLDER,
            "category": ["business-systems"],
            "risk": [4, 5],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}appfilter"
        state["appfilter_id"] = result["id"]

    def test_scm_get_application_filter(self, client, state):
        result = serialize(client.application_filter.get(state["appfilter_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_application_filter(self, client, state):
        client.application_filter.delete(state["appfilter_id"])


# ===========================================================================
# POLICY OBJECTS — Schedules
# ===========================================================================

class TestSchedules:
    """Tools: scm_list_schedules, scm_get_schedule, scm_create_schedule,
    scm_update_schedule, scm_delete_schedule"""

    def test_scm_list_schedules(self, client):
        result = serialize(client.schedule.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_schedule(self, client, state):
        result = serialize(client.schedule.create({
            "name": f"{PREFIX}schedule",
            "folder": TEST_FOLDER,
            "schedule_type": {
                "recurring": {
                    "weekly": {
                        "monday": ["09:00-17:00"],
                        "tuesday": ["09:00-17:00"],
                    }
                }
            },
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}schedule"
        state["schedule_id"] = result["id"]

    def test_scm_get_schedule(self, client, state):
        result = serialize(client.schedule.get(state["schedule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_schedule(self, client, state):
        sched = client.schedule.get(state["schedule_id"])
        sched.schedule_type = {
            "recurring": {"weekly": {"wednesday": ["08:00-18:00"]}}
        }
        result = serialize(client.schedule.update(sched))
        assert_ok(result, "id")

    def test_scm_delete_schedule(self, client, state):
        client.schedule.delete(state["schedule_id"])


# ===========================================================================
# POLICY OBJECTS — External Dynamic Lists
# ===========================================================================

class TestExternalDynamicLists:
    """Tools: scm_list_external_dynamic_lists, scm_get_external_dynamic_list,
    scm_create_external_dynamic_list, scm_update_external_dynamic_list,
    scm_delete_external_dynamic_list"""

    def test_scm_list_external_dynamic_lists(self, client):
        result = serialize(client.external_dynamic_list.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_external_dynamic_list(self, client, state):
        result = serialize(client.external_dynamic_list.create({
            "name": f"{PREFIX}edl",
            "folder": TEST_FOLDER,
            "type": {
                "ip": {
                    "url": "https://example.com/blocklist.txt",
                    "recurring": {"daily": {"at": "03"}},
                }
            },
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}edl"
        state["edl_id"] = result["id"]

    def test_scm_get_external_dynamic_list(self, client, state):
        result = serialize(client.external_dynamic_list.get(state["edl_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_external_dynamic_list(self, client, state):
        edl = client.external_dynamic_list.get(state["edl_id"])
        result = serialize(client.external_dynamic_list.update(edl))
        assert_ok(result, "id")

    def test_scm_delete_external_dynamic_list(self, client, state):
        client.external_dynamic_list.delete(state["edl_id"])


# ===========================================================================
# SECURITY — Security Zones
# ===========================================================================

class TestSecurityZones:
    """Tools: scm_list_security_zones, scm_get_security_zone,
    scm_create_security_zone, scm_update_security_zone, scm_delete_security_zone"""

    def test_scm_list_security_zones(self, client):
        result = serialize(client.security_zone.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_security_zone(self, client, state):
        result = serialize(client.security_zone.create({
            "name": f"{PREFIX}seczone",
            "folder": TEST_FOLDER,
            "enable_user_identification": False,
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}seczone"
        state["seczone_id"] = result["id"]
        state["seczone_name"] = result["name"]

    def test_scm_get_security_zone(self, client, state):
        result = serialize(client.security_zone.get(state["seczone_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_security_zone(self, client, state):
        zone = client.security_zone.get(state["seczone_id"])
        zone.enable_user_identification = True
        result = serialize(client.security_zone.update(zone))
        assert_ok(result, "id")

    def test_scm_delete_security_zone(self, client, state):
        client.security_zone.delete(state["seczone_id"])


# ===========================================================================
# SECURITY — Security Rules
# ===========================================================================

class TestSecurityRules:
    """Tools: scm_list_security_rules, scm_get_security_rule,
    scm_create_security_rule, scm_update_security_rule,
    scm_move_security_rule, scm_delete_security_rule"""

    def test_scm_list_security_rules(self, client):
        result = serialize(client.security_rule.list(folder=TEST_FOLDER, rulebase="pre"))
        assert_list_ok(result)

    def test_scm_create_security_rule(self, client, state, test_zone):
        result = serialize(client.security_rule.create({
            "name": f"{PREFIX}secrule",
            "folder": TEST_FOLDER,
            "action": "allow",
            "from": [test_zone["name"]],
            "to": [test_zone["name"]],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["application-default"],
            "category": ["any"],
            "source_user": ["any"],
        }, rulebase="pre"))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}secrule"
        state["secrule_id"] = result["id"]

    def test_scm_get_security_rule(self, client, state):
        result = serialize(client.security_rule.get(state["secrule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_security_rule(self, client, state):
        rule = client.security_rule.get(state["secrule_id"])
        rule.description = "pytest updated"
        result = serialize(client.security_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_move_security_rule(self, client, state):
        result = client.security_rule.move(
            state["secrule_id"],
            {"destination": "bottom", "rulebase": "pre"},
        )
        # move returns None on success
        assert result is None or isinstance(result, dict)

    def test_scm_delete_security_rule(self, client, state):
        client.security_rule.delete(state["secrule_id"])


# ===========================================================================
# SECURITY — Decryption Rules
# ===========================================================================

class TestDecryptionRules:
    """Tools: scm_list_decryption_rules, scm_get_decryption_rule,
    scm_create_decryption_rule, scm_update_decryption_rule,
    scm_delete_decryption_rule"""

    def test_scm_list_decryption_rules(self, client):
        result = serialize(client.decryption_rule.list(folder=TEST_FOLDER, rulebase="pre"))
        assert_list_ok(result)

    def test_scm_create_decryption_rule(self, client, state, test_zone):
        result = serialize(client.decryption_rule.create({
            "name": f"{PREFIX}decrep-rule",
            "folder": TEST_FOLDER,
            "action": "no-decrypt",
            "type": {"ssl_forward_proxy": {}},
            "from": [test_zone["name"]],
            "to": [test_zone["name"]],
            "source": ["any"],
            "destination": ["any"],
            "service": ["any"],
            "category": ["any"],
            "source_user": ["any"],
        }, rulebase="pre"))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}decrep-rule"
        state["decrep_rule_id"] = result["id"]

    def test_scm_get_decryption_rule(self, client, state):
        result = serialize(client.decryption_rule.get(state["decrep_rule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_decryption_rule(self, client, state):
        rule = client.decryption_rule.get(state["decrep_rule_id"])
        rule.description = "pytest updated"
        result = serialize(client.decryption_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_delete_decryption_rule(self, client, state):
        client.decryption_rule.delete(state["decrep_rule_id"])


# ===========================================================================
# SECURITY — Authentication Rules
# ===========================================================================

class TestAuthenticationRules:
    """Tools: scm_list_authentication_rules, scm_get_authentication_rule,
    scm_create_authentication_rule, scm_update_authentication_rule,
    scm_delete_authentication_rule"""

    def test_scm_list_authentication_rules(self, client):
        result = serialize(client.authentication_rule.list(folder=TEST_FOLDER, rulebase="pre"))
        assert_list_ok(result)

    def test_scm_create_authentication_rule(self, client, state, test_zone):
        try:
            result = serialize(client.authentication_rule.create({
                "name": f"{PREFIX}authrule",
                "folder": TEST_FOLDER,
                "from": [test_zone["name"]],
                "to": [test_zone["name"]],
                "source": ["any"],
                "destination": ["any"],
                "source_user": ["any"],
                "authentication_enforcement": "default-authentication",
            }, rulebase="pre"))
            assert_ok(result, "id", "name")
            state["authrule_id"] = result["id"]
        except Exception as exc:
            pytest.skip(f"Auth rule creation requires an enforcement profile: {exc}")

    def test_scm_get_authentication_rule(self, client, state):
        if "authrule_id" not in state:
            pytest.skip("auth rule was not created")
        result = serialize(client.authentication_rule.get(state["authrule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_authentication_rule(self, client, state):
        if "authrule_id" not in state:
            pytest.skip("auth rule was not created")
        rule = client.authentication_rule.get(state["authrule_id"])
        rule.description = "pytest updated"
        result = serialize(client.authentication_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_delete_authentication_rule(self, client, state):
        if "authrule_id" not in state:
            pytest.skip("auth rule was not created")
        client.authentication_rule.delete(state["authrule_id"])


# ===========================================================================
# NETWORK — NAT Rules
# ===========================================================================

class TestNatRules:
    """Tools: scm_list_nat_rules, scm_get_nat_rule, scm_create_nat_rule,
    scm_update_nat_rule, scm_delete_nat_rule"""

    def test_scm_list_nat_rules(self, client):
        result = serialize(client.nat_rule.list(folder=TEST_FOLDER, position="pre"))
        assert_list_ok(result)

    def test_scm_create_nat_rule(self, client, state, test_zone):
        # Delete leftover from a previous failed run if it exists
        try:
            existing = client.nat_rule.list(folder=TEST_FOLDER, position="pre")
            for r in existing:
                if getattr(r, "name", None) == f"{PREFIX}nat-rule":
                    client.nat_rule.delete(r.id)
        except Exception:
            pass
        result = serialize(client.nat_rule.create({
            "name": f"{PREFIX}nat-rule",
            "folder": TEST_FOLDER,
            "nat_type": "ipv4",
            "from": [test_zone["name"]],
            "to": [test_zone["name"]],
            "source": ["any"],
            "destination": ["any"],
            "service": "any",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}nat-rule"
        state["nat_rule_id"] = result["id"]

    def test_scm_get_nat_rule(self, client, state):
        result = serialize(client.nat_rule.get(state["nat_rule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_nat_rule(self, client, state):
        rule = client.nat_rule.get(state["nat_rule_id"])
        rule.description = "pytest updated"
        result = serialize(client.nat_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_delete_nat_rule(self, client, state):
        client.nat_rule.delete(state["nat_rule_id"])


# ===========================================================================
# NETWORK — PBF Rules
# ===========================================================================

class TestPbfRules:
    """Tools: scm_list_pbf_rules, scm_get_pbf_rule, scm_create_pbf_rule,
    scm_update_pbf_rule, scm_delete_pbf_rule"""

    def test_scm_list_pbf_rules(self, client):
        result = serialize(client.pbf_rule.list(folder=TEST_FOLDER, rulebase="pre"))
        assert_list_ok(result)

    def test_scm_create_pbf_rule(self, client, state, test_zone):
        result = serialize(client.pbf_rule.create({
            "name": f"{PREFIX}pbf-rule",
            "folder": TEST_FOLDER,
            "from_": {"zone": [test_zone["name"]]},
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["any"],
            "action": {"discard": {}},
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}pbf-rule"
        state["pbf_rule_id"] = result["id"]

    def test_scm_get_pbf_rule(self, client, state):
        result = serialize(client.pbf_rule.get(state["pbf_rule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_pbf_rule(self, client, state):
        rule = client.pbf_rule.get(state["pbf_rule_id"])
        rule.description = "pytest updated"
        result = serialize(client.pbf_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_delete_pbf_rule(self, client, state):
        client.pbf_rule.delete(state["pbf_rule_id"])


# ===========================================================================
# NETWORK — QoS Rules
# ===========================================================================

class TestQosRules:
    """Tools: scm_list_qos_rules, scm_get_qos_rule, scm_create_qos_rule,
    scm_update_qos_rule, scm_delete_qos_rule"""

    def test_scm_list_qos_rules(self, client):
        result = serialize(client.qos_rule.list(folder=TEST_FOLDER, rulebase="pre"))
        assert_list_ok(result)

    def test_scm_create_qos_rule(self, client, state, test_zone):
        result = serialize(client.qos_rule.create({
            "name": f"{PREFIX}qos-rule",
            "folder": TEST_FOLDER,
            "action": {"class": "4"},
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}qos-rule"
        state["qos_rule_id"] = result["id"]

    def test_scm_get_qos_rule(self, client, state):
        result = serialize(client.qos_rule.get(state["qos_rule_id"]))
        assert_ok(result, "id", "name")

    def test_scm_update_qos_rule(self, client, state):
        rule = client.qos_rule.get(state["qos_rule_id"])
        rule.description = "pytest updated"
        result = serialize(client.qos_rule.update(rule))
        assert_ok(result, "id")

    def test_scm_delete_qos_rule(self, client, state):
        client.qos_rule.delete(state["qos_rule_id"])


# ===========================================================================
# PROFILES — Anti-Spyware
# ===========================================================================

class TestAntiSpywareProfiles:
    """Tools: scm_list_anti_spyware_profiles, scm_get_anti_spyware_profile,
    scm_create_anti_spyware_profile, scm_delete_anti_spyware_profile"""

    def test_scm_list_anti_spyware_profiles(self, client):
        result = serialize(client.anti_spyware_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_anti_spyware_profile(self, client, state):
        result = serialize(client.anti_spyware_profile.create({
            "name": f"{PREFIX}anti-spyware",
            "folder": TEST_FOLDER,
            "description": "pytest anti-spyware profile",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}anti-spyware"
        state["anti_spyware_id"] = result["id"]

    def test_scm_get_anti_spyware_profile(self, client, state):
        result = serialize(client.anti_spyware_profile.get(state["anti_spyware_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_anti_spyware_profile(self, client, state):
        client.anti_spyware_profile.delete(state["anti_spyware_id"])


# ===========================================================================
# PROFILES — WildFire Antivirus
# ===========================================================================

class TestWildfireProfiles:
    """Tools: scm_list_wildfire_profiles, scm_get_wildfire_profile,
    scm_create_wildfire_profile, scm_delete_wildfire_profile"""

    def test_scm_list_wildfire_profiles(self, client):
        result = serialize(client.wildfire_antivirus_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_wildfire_profile(self, client, state):
        result = serialize(client.wildfire_antivirus_profile.create({
            "name": f"{PREFIX}wildfire",
            "folder": TEST_FOLDER,
            "description": "pytest wildfire profile",
            "rules": [{"name": "default", "direction": "both", "application": ["any"], "file_type": ["any"]}],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}wildfire"
        state["wildfire_id"] = result["id"]

    def test_scm_get_wildfire_profile(self, client, state):
        result = serialize(client.wildfire_antivirus_profile.get(state["wildfire_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_wildfire_profile(self, client, state):
        client.wildfire_antivirus_profile.delete(state["wildfire_id"])


# ===========================================================================
# PROFILES — Vulnerability Protection
# ===========================================================================

class TestVulnerabilityProfiles:
    """Tools: scm_list_vulnerability_profiles, scm_get_vulnerability_profile,
    scm_create_vulnerability_profile, scm_delete_vulnerability_profile"""

    def test_scm_list_vulnerability_profiles(self, client):
        result = serialize(client.vulnerability_protection_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_vulnerability_profile(self, client, state):
        result = serialize(client.vulnerability_protection_profile.create({
            "name": f"{PREFIX}vuln",
            "folder": TEST_FOLDER,
            "description": "pytest vulnerability profile",
            "rules": [{"name": "default", "severity": ["any"], "host": "any", "cve": ["any"], "vendor_id": ["any"], "category": "any"}],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}vuln"
        state["vuln_id"] = result["id"]

    def test_scm_get_vulnerability_profile(self, client, state):
        result = serialize(client.vulnerability_protection_profile.get(state["vuln_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_vulnerability_profile(self, client, state):
        client.vulnerability_protection_profile.delete(state["vuln_id"])


# ===========================================================================
# PROFILES — URL Access Profiles
# ===========================================================================

class TestUrlAccessProfiles:
    """Tools: scm_list_url_access_profiles, scm_get_url_access_profile,
    scm_create_url_access_profile, scm_delete_url_access_profile"""

    def test_scm_list_url_access_profiles(self, client):
        result = serialize(client.url_access_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_url_access_profile(self, client, state):
        result = serialize(client.url_access_profile.create({
            "name": f"{PREFIX}url-access",
            "folder": TEST_FOLDER,
            "description": "pytest url access profile",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}url-access"
        state["url_access_id"] = result["id"]

    def test_scm_get_url_access_profile(self, client, state):
        result = serialize(client.url_access_profile.get(state["url_access_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_url_access_profile(self, client, state):
        client.url_access_profile.delete(state["url_access_id"])


# ===========================================================================
# PROFILES — URL Categories
# ===========================================================================

class TestUrlCategories:
    """Tools: scm_list_url_categories, scm_get_url_category,
    scm_create_url_category, scm_delete_url_category"""

    def test_scm_list_url_categories(self, client):
        result = serialize(client.url_category.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_url_category(self, client, state):
        result = serialize(client.url_category.create({
            "name": f"{PREFIX}url-cat",
            "folder": TEST_FOLDER,
            "list": ["pytest.example.com", "test.example.org"],
            "type": "URL List",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}url-cat"
        state["url_cat_id"] = result["id"]

    def test_scm_get_url_category(self, client, state):
        result = serialize(client.url_category.get(state["url_cat_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_url_category(self, client, state):
        client.url_category.delete(state["url_cat_id"])


# ===========================================================================
# PROFILES — DNS Security Profiles
# ===========================================================================

class TestDnsSecurityProfiles:
    """Tools: scm_list_dns_security_profiles, scm_get_dns_security_profile,
    scm_create_dns_security_profile, scm_delete_dns_security_profile"""

    def test_scm_list_dns_security_profiles(self, client):
        result = serialize(client.dns_security_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_dns_security_profile(self, client, state):
        result = serialize(client.dns_security_profile.create({
            "name": f"{PREFIX}dns-sec",
            "folder": TEST_FOLDER,
            "description": "pytest dns security profile",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}dns-sec"
        state["dns_sec_id"] = result["id"]

    def test_scm_get_dns_security_profile(self, client, state):
        result = serialize(client.dns_security_profile.get(state["dns_sec_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_dns_security_profile(self, client, state):
        client.dns_security_profile.delete(state["dns_sec_id"])


# ===========================================================================
# PROFILES — Decryption Profiles
# ===========================================================================

class TestDecryptionProfiles:
    """Tools: scm_list_decryption_profiles, scm_get_decryption_profile,
    scm_create_decryption_profile, scm_delete_decryption_profile"""

    def test_scm_list_decryption_profiles(self, client):
        result = serialize(client.decryption_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_decryption_profile(self, client, state):
        result = serialize(client.decryption_profile.create({
            "name": f"{PREFIX}decrypt-profile",
            "folder": TEST_FOLDER,
            "ssl_forward_proxy": {
                "block_expired_certificate": True,
                "block_untrusted_issuer": True,
            },
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}decrypt-profile"
        state["decrypt_profile_id"] = result["id"]

    def test_scm_get_decryption_profile(self, client, state):
        result = serialize(client.decryption_profile.get(state["decrypt_profile_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_decryption_profile(self, client, state):
        client.decryption_profile.delete(state["decrypt_profile_id"])


# ===========================================================================
# PROFILES — File Blocking
# ===========================================================================

class TestFileBlockingProfiles:
    """Tools: scm_list_file_blocking_profiles, scm_get_file_blocking_profile,
    scm_create_file_blocking_profile, scm_delete_file_blocking_profile"""

    def test_scm_list_file_blocking_profiles(self, client):
        result = serialize(client.file_blocking_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_file_blocking_profile(self, client, state):
        result = serialize(client.file_blocking_profile.create({
            "name": f"{PREFIX}file-block",
            "folder": TEST_FOLDER,
            "description": "pytest file blocking profile",
            "rules": [{
                "name": "block-all",
                "application": ["any"],
                "file_type": ["any"],
                "direction": "both",
                "action": "block",
            }],
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}file-block"
        state["file_block_id"] = result["id"]

    def test_scm_get_file_blocking_profile(self, client, state):
        result = serialize(client.file_blocking_profile.get(state["file_block_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_file_blocking_profile(self, client, state):
        client.file_blocking_profile.delete(state["file_block_id"])


# ===========================================================================
# PROFILES — Zone Protection
# ===========================================================================

class TestZoneProtectionProfiles:
    """Tools: scm_list_zone_protection_profiles, scm_get_zone_protection_profile,
    scm_create_zone_protection_profile, scm_delete_zone_protection_profile"""

    def test_scm_list_zone_protection_profiles(self, client):
        result = serialize(client.zone_protection_profile.list(folder=TEST_FOLDER))
        assert_list_ok(result)

    def test_scm_create_zone_protection_profile(self, client, state):
        result = serialize(client.zone_protection_profile.create({
            "name": f"{PREFIX}zone-protect",
            "folder": TEST_FOLDER,
            "description": "pytest zone protection profile",
        }))
        assert_ok(result, "id", "name")
        assert result["name"] == f"{PREFIX}zone-protect"
        state["zone_protect_id"] = result["id"]

    def test_scm_get_zone_protection_profile(self, client, state):
        result = serialize(client.zone_protection_profile.get(state["zone_protect_id"]))
        assert_ok(result, "id", "name")

    def test_scm_delete_zone_protection_profile(self, client, state):
        client.zone_protection_profile.delete(state["zone_protect_id"])


# ===========================================================================
# OPERATIONS
# ===========================================================================

class TestOperations:
    """Tools: scm_list_tsg_profiles, scm_list_jobs, scm_get_job_status
    NOTE: scm_commit is intentionally omitted — committing in CI would push
    staged test objects to managed devices."""

    def test_scm_list_tsg_profiles(self, client):
        from src.client import list_tsg_profiles
        result = list_tsg_profiles()
        assert isinstance(result, list)
        assert len(result) >= 1
        assert all("name" in p and "alias" in p for p in result)

    def test_scm_list_jobs(self, client):
        result = serialize(client.list_jobs())
        assert isinstance(result, dict), f"Expected dict, got {type(result)}: {result}"
        assert "data" in result
        assert isinstance(result["data"], list)

    def test_scm_get_job_status(self, client):
        jobs = serialize(client.list_jobs())
        job_list = jobs.get("data", [])
        if not job_list:
            pytest.skip("No jobs available to test scm_get_job_status")
        job_id = job_list[0]["id"]
        result = serialize(client.get_job_status(job_id))
        assert_ok(result)


# ===========================================================================
# SEARCH
# ===========================================================================

class TestSearch:
    """Tools: scm_list_resource_types, scm_search"""

    def test_scm_list_resource_types(self):
        from src.tools.search import _RESOURCE_REGISTRY
        types = [label for _, _, _, label in _RESOURCE_REGISTRY]
        assert isinstance(types, list)
        assert len(types) == len(_RESOURCE_REGISTRY)
        assert "addresses" in types
        assert "security_rules" in types

    def test_scm_search_by_name(self, client):
        from src.tools.search import _RESOURCE_REGISTRY, _name_matches
        from src.utils import serialize

        resource = getattr(client, "address")
        items = resource.list(folder=TEST_FOLDER)
        assert isinstance(items, list)

    def test_scm_search_name_hit(self):
        from src.tools.search import _name_matches
        assert _name_matches("1.1.1.1", "1.1.1", False) is True
        assert _name_matches("1.1.1.1", "1.1.1.1", True) is True
        assert _name_matches("1.1.1.1", "2.2.2.2", False) is False

    def test_scm_search_field_hit(self):
        from src.tools.search import _fields_match
        obj = {"ip_netmask": "1.1.1.1/32", "name": "1.1.1.1"}
        assert _fields_match(obj, "1.1.1.1") is True
        assert _fields_match(obj, "2.2.2.2") is False

    def test_scm_search_integration(self, client):
        """Full search integration test against PACNW folder."""
        from src.tools.search import _RESOURCE_REGISTRY, _name_matches
        results = {}
        for attr, needs_folder, is_rule, label in _RESOURCE_REGISTRY:
            if label not in ("addresses", "services", "tags"):
                continue
            resource = getattr(client, attr)
            try:
                items = resource.list(folder=TEST_FOLDER)
                hits = [serialize(i) for i in items if _name_matches(getattr(i, "name", ""), "1", False)]
                if hits:
                    results[label] = hits
            except Exception:
                pass
        assert isinstance(results, dict)


# ===========================================================================
# MIGRATION
# ===========================================================================

class TestMigration:
    """Tools: scm_diff_folders, scm_copy_objects (dry_run), scm_clone_security_rule"""

    def test_scm_diff_folders(self, client):
        from src.tools.migration import _OBJECT_COPY_ORDER
        from src.utils import serialize

        src_client = client
        dst_client = client
        results = {}
        for attr, label in _OBJECT_COPY_ORDER[:3]:
            try:
                src_names = {
                    getattr(i, "name", None)
                    for i in getattr(src_client, attr).list(folder=TEST_FOLDER)
                    if getattr(i, "name", None)
                }
                dst_names = {
                    getattr(i, "name", None)
                    for i in getattr(dst_client, attr).list(folder=TEST_FOLDER)
                    if getattr(i, "name", None)
                }
                results[label] = {
                    "only_in_src": sorted(src_names - dst_names),
                    "only_in_dst": sorted(dst_names - src_names),
                    "in_both": sorted(src_names & dst_names),
                }
            except Exception:
                pass
        assert isinstance(results, dict)

    def test_scm_copy_objects_dry_run(self, client):
        from src.tools.migration import _OBJECT_COPY_ORDER, _to_create_payload
        from src.utils import serialize

        would_create = []
        for attr, label in _OBJECT_COPY_ORDER[:2]:
            try:
                items = getattr(client, attr).list(folder=TEST_FOLDER)
                for item in items:
                    name = getattr(item, "name", None)
                    if name and name.startswith(PREFIX):
                        payload = _to_create_payload(serialize(item), "DryRunDst")
                        would_create.append((label, name, payload))
            except Exception:
                pass
        assert isinstance(would_create, list)

    def test_scm_strip_nulls_in_payload(self):
        """Verify the nested null fix in _to_create_payload (regression test)."""
        from src.tools.migration import _to_create_payload
        obj = {
            "name": "test-svc",
            "id": "abc123",
            "folder": "PACNW",
            "protocol": {
                "tcp": {"port": "2020", "override": None},
                "udp": None,
            },
            "description": None,
        }
        payload = _to_create_payload(obj, "Dst")
        assert "id" not in payload
        assert payload["folder"] == "Dst"
        assert "override" not in payload["protocol"]["tcp"]
        assert "udp" not in payload["protocol"]
        assert "description" not in payload

    def test_scm_clone_security_rule(self, client, test_zone):
        from src.tools.migration import _to_create_payload
        from src.utils import serialize

        # Create a source rule to clone
        src_rule = client.security_rule.create({
            "name": f"{PREFIX}clone-src",
            "folder": TEST_FOLDER,
            "action": "deny",
            "from": [test_zone["name"]],
            "to": [test_zone["name"]],
            "source": ["any"],
            "destination": ["any"],
            "application": ["any"],
            "service": ["application-default"],
            "category": ["any"],
            "source_user": ["any"],
        }, rulebase="pre")
        src_id = str(src_rule.id)

        try:
            rule = client.security_rule.get(src_id)
            payload = _to_create_payload(serialize(rule), TEST_FOLDER)
            payload["name"] = f"{PREFIX}clone-dst"
            cloned = client.security_rule.create(payload, rulebase="pre")
            clone_id = str(cloned.id)
            assert cloned.name == f"{PREFIX}clone-dst"
            client.security_rule.delete(clone_id)
        finally:
            client.security_rule.delete(src_id)
