"""Tools for global search across SCM resource types."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize

# All searchable resource types and how to list them.
# Each entry: (accessor_attr, list_kwargs_fn, label)
# list_kwargs_fn receives (folder, rulebase) and returns kwargs for .list()
_RESOURCE_REGISTRY: list[tuple[str, callable, str]] = [
    # Setup
    ("folder",                      lambda f, r: {},                            "folders"),
    ("snippet",                     lambda f, r: {},                            "snippets"),
    # Objects
    ("address",                     lambda f, r: {"folder": f},                 "addresses"),
    ("address_group",               lambda f, r: {"folder": f},                 "address_groups"),
    ("service",                     lambda f, r: {"folder": f},                 "services"),
    ("service_group",               lambda f, r: {"folder": f},                 "service_groups"),
    ("tag",                         lambda f, r: {"folder": f},                 "tags"),
    ("log_forwarding_profile",      lambda f, r: {"folder": f},                 "log_forwarding_profiles"),
    ("http_server_profile",         lambda f, r: {"folder": f},                 "http_server_profiles"),
    ("syslog_server_profile",       lambda f, r: {"folder": f},                 "syslog_server_profiles"),
    # Policy objects
    ("application",                 lambda f, r: {"folder": f},                 "applications"),
    ("application_group",           lambda f, r: {"folder": f},                 "application_groups"),
    ("application_filter",          lambda f, r: {"folder": f},                 "application_filters"),
    ("schedule",                    lambda f, r: {"folder": f},                 "schedules"),
    ("external_dynamic_list",       lambda f, r: {"folder": f},                 "external_dynamic_lists"),
    # Security rules
    ("security_rule",               lambda f, r: {"folder": f, "rulebase": r},  "security_rules"),
    ("decryption_rule",             lambda f, r: {"folder": f, "rulebase": r},  "decryption_rules"),
    ("authentication_rule",         lambda f, r: {"folder": f, "rulebase": r},  "authentication_rules"),
    # Network rules
    ("nat_rule",                    lambda f, r: {"folder": f, "position": r},  "nat_rules"),
    ("pbf_rule",                    lambda f, r: {"folder": f, "rulebase": r},  "pbf_rules"),
    ("qos_rule",                    lambda f, r: {"folder": f, "rulebase": r},  "qos_rules"),
    # Security zones
    ("security_zone",               lambda f, r: {"folder": f},                 "security_zones"),
    # Profiles
    ("anti_spyware_profile",        lambda f, r: {"folder": f},                 "anti_spyware_profiles"),
    ("wildfire_antivirus_profile",  lambda f, r: {"folder": f},                 "wildfire_profiles"),
    ("vulnerability_protection_profile", lambda f, r: {"folder": f},           "vulnerability_profiles"),
    ("url_access_profile",          lambda f, r: {"folder": f},                 "url_access_profiles"),
    ("url_category",                lambda f, r: {"folder": f},                 "url_categories"),
    ("dns_security_profile",        lambda f, r: {"folder": f},                 "dns_security_profiles"),
    ("decryption_profile",          lambda f, r: {"folder": f},                 "decryption_profiles"),
    ("file_blocking_profile",       lambda f, r: {"folder": f},                 "file_blocking_profiles"),
    ("zone_protection_profile",     lambda f, r: {"folder": f},                 "zone_protection_profiles"),
]

# Resource types that don't require a folder (global scope)
_NO_FOLDER_TYPES = {"folders", "snippets"}


def _matches(name: str, query: str, exact: bool) -> bool:
    if exact:
        return name == query
    return query.lower() in name.lower()


def register(mcp: FastMCP) -> None:
    """Register global search tools on the given FastMCP instance."""

    @mcp.tool()
    def scm_search(
        query: str,
        folder: str = "All",
        resource_types: list[str] | None = None,
        exact_match: bool = False,
        include_rulebases: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Search for objects and rules by name across all (or selected) SCM resource types.

        Performs a case-insensitive substring search by default. Returns a dict keyed
        by resource type containing all matching objects.

        Args:
            query: Name to search for (substring match by default).
            folder: Folder to search in (default 'All'). Ignored for folders/snippets
                which are always global.
            resource_types: Optional list of resource type names to limit the search.
                Omit to search all types. Valid values:
                folders, snippets, addresses, address_groups, services, service_groups,
                tags, log_forwarding_profiles, http_server_profiles, syslog_server_profiles,
                applications, application_groups, application_filters, schedules,
                external_dynamic_lists, security_rules, decryption_rules,
                authentication_rules, nat_rules, pbf_rules, qos_rules, security_zones,
                anti_spyware_profiles, wildfire_profiles, vulnerability_profiles,
                url_access_profiles, url_categories, dns_security_profiles,
                decryption_profiles, file_blocking_profiles, zone_protection_profiles.
            exact_match: If True, only return objects whose name exactly equals query
                (case-sensitive). Default False.
            include_rulebases: For rule types, which rulebases to search.
                Default ['pre', 'post']. Pass ['pre'] or ['post'] to limit.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        rulebases = include_rulebases or ["pre", "post"]
        client = get_client(tsg_id)
        results: dict[str, list[dict]] = {}
        errors: dict[str, str] = {}

        target_labels = set(resource_types) if resource_types else None

        for attr, kwargs_fn, label in _RESOURCE_REGISTRY:
            if target_labels and label not in target_labels:
                continue

            resource = getattr(client, attr)
            folder_arg = None if label in _NO_FOLDER_TYPES else folder

            # Rule types iterate over rulebases; others run once
            if label in ("security_rules", "decryption_rules", "authentication_rules",
                         "pbf_rules", "qos_rules"):
                iters = rulebases
            elif label == "nat_rules":
                iters = rulebases
            else:
                iters = [None]

            matches: list[dict] = []
            for rulebase in iters:
                try:
                    kwargs = kwargs_fn(folder_arg, rulebase)
                    # Remove None-valued keys (e.g. folder for global types)
                    kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    items = resource.list(**kwargs)
                    for item in items:
                        name = getattr(item, "name", None)
                        if name and _matches(name, query, exact_match):
                            serialized = serialize(item)
                            if rulebase:
                                serialized["_rulebase"] = rulebase
                            matches.append(serialized)
                except Exception as exc:
                    errors[label] = str(exc)
                    break

            if matches:
                results[label] = matches

        response: dict = {"query": query, "folder": folder, "results": results}
        if errors:
            response["errors"] = errors
        response["total_matches"] = sum(len(v) for v in results.values())
        return response

    @mcp.tool()
    def scm_list_resource_types() -> list[str]:
        """List all resource type names valid for use with scm_search.

        Returns the complete list of searchable resource type names that can be
        passed as the resource_types argument to scm_search.
        """
        return [label for _, _, label in _RESOURCE_REGISTRY]
