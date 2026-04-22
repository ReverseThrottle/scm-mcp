"""Tools for global search across SCM resource types."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.tools.objects import _list_tags_raw
from src.utils import handle_error, serialize

# All searchable resource types.
# Each entry: (accessor_attr, needs_folder, is_rule, label)
# is_rule=True means the list() call takes rulebase/position and we iterate per rulebase.
# is_rule="nat" uses position= instead of rulebase=.
_RESOURCE_REGISTRY: list[tuple[str, bool, str | bool, str]] = [
    # Setup (global scope — no folder required)
    ("folder",                           False, False, "folders"),
    ("snippet",                          False, False, "snippets"),
    # Objects
    ("address",                          True,  False, "addresses"),
    ("address_group",                    True,  False, "address_groups"),
    ("service",                          True,  False, "services"),
    ("service_group",                    True,  False, "service_groups"),
    ("tag",                              True,  False, "tags"),
    ("log_forwarding_profile",           True,  False, "log_forwarding_profiles"),
    ("http_server_profile",              True,  False, "http_server_profiles"),
    ("syslog_server_profile",            True,  False, "syslog_server_profiles"),
    # Policy objects
    ("application",                      True,  False, "applications"),
    ("application_group",                True,  False, "application_groups"),
    ("application_filter",               True,  False, "application_filters"),
    ("schedule",                         True,  False, "schedules"),
    ("external_dynamic_list",            True,  False, "external_dynamic_lists"),
    # Security rules
    ("security_rule",                    True,  True,  "security_rules"),
    ("decryption_rule",                  True,  True,  "decryption_rules"),
    ("authentication_rule",              True,  True,  "authentication_rules"),
    # Network rules
    ("nat_rule",                         True,  "nat", "nat_rules"),
    ("pbf_rule",                         True,  True,  "pbf_rules"),
    ("qos_rule",                         True,  True,  "qos_rules"),
    # Security zones
    ("security_zone",                    True,  False, "security_zones"),
    # Profiles
    ("anti_spyware_profile",             True,  False, "anti_spyware_profiles"),
    ("wildfire_antivirus_profile",       True,  False, "wildfire_profiles"),
    ("vulnerability_protection_profile", True,  False, "vulnerability_profiles"),
    ("url_access_profile",               True,  False, "url_access_profiles"),
    ("url_category",                     True,  False, "url_categories"),
    ("dns_security_profile",             True,  False, "dns_security_profiles"),
    ("decryption_profile",               True,  False, "decryption_profiles"),
    ("file_blocking_profile",            True,  False, "file_blocking_profiles"),
    ("zone_protection_profile",          True,  False, "zone_protection_profiles"),
]

# String fields to scan when search_fields=True (covers rules and common objects)
_FIELD_SCAN_KEYS = {
    "source", "destination", "application", "service",
    "from", "to", "from_",           # rule zones (from_ is the Python alias)
    "static",                         # address group members
    "members",                        # service/app group members
    "ip_netmask", "ip_range", "fqdn", "ip_wildcard",  # address values
    "list",                           # url category entries
    "profile_setting", "log_setting",
}


def _name_matches(name: str, query: str, exact: bool) -> bool:
    if exact:
        return name == query
    return query.lower() in name.lower()


def _fields_match(obj: dict, query: str) -> bool:
    """Return True if query appears in any scannable field value of obj."""
    q = query.lower()
    for key, val in obj.items():
        if key not in _FIELD_SCAN_KEYS:
            continue
        if isinstance(val, str) and q in val.lower():
            return True
        if isinstance(val, list):
            for item in val:
                if isinstance(item, str) and q in item.lower():
                    return True
        if isinstance(val, dict):
            # e.g. profile_setting = {"group": ["best-practice"]}
            for inner in val.values():
                if isinstance(inner, str) and q in inner.lower():
                    return True
                if isinstance(inner, list):
                    for item in inner:
                        if isinstance(item, str) and q in item.lower():
                            return True
    return False


def _list_resource(resource, needs_folder: bool, is_rule, folder: str | None,
                   snippet: str | None, rulebase: str, tags: list[str] | None) -> list:
    """Call resource.list() with the right kwargs for this resource type."""
    # Tags have a strict name-pattern validator that rejects the whole batch on one
    # invalid name. Use the raw helper which parses per-item and skips bad names.
    if hasattr(resource, "ENDPOINT") and resource.ENDPOINT == "/config/objects/v1/tags":
        raw = _list_tags_raw(resource, folder=folder, snippet=snippet)
        # Return lightweight objects that expose .name and serialize cleanly
        return [_RawItem(r) for r in raw]

    kwargs: dict = {}

    if needs_folder:
        if snippet:
            kwargs["snippet"] = snippet
        elif folder:
            kwargs["folder"] = folder

    if is_rule is True:
        kwargs["rulebase"] = rulebase
    elif is_rule == "nat":
        kwargs["position"] = rulebase

    if tags:
        kwargs["tags"] = tags

    return resource.list(**kwargs)


class _RawItem(dict):
    """dict subclass so serialize() handles it as a plain dict while .name attribute access works."""

    def __getattr__(self, name: str):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


def register(mcp: FastMCP) -> None:
    """Register global search tools on the given FastMCP instance."""

    @mcp.tool()
    def scm_search(
        query: str,
        folder: str = "All",
        folders: list[str] | None = None,
        snippet: str | None = None,
        resource_types: list[str] | None = None,
        exact_match: bool = False,
        search_fields: bool = False,
        tags: list[str] | None = None,
        include_rulebases: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Search for objects and rules by name (and optionally field values) across SCM.

        Performs a case-insensitive substring search by default. Returns results grouped
        by resource type. Errors per type are reported separately so partial results
        are always returned.

        Args:
            query: String to search for. Matched against object names by default;
                also matched against field values when search_fields=True.
            folder: Single folder to search (default 'All'). Ignored when folders or
                snippet is provided. Ignored for global types (folders, snippets).
            folders: Search multiple folders in one call. Results are deduplicated by
                object ID across folders. Overrides the folder param when provided.
            snippet: Search within a snippet scope instead of a folder. Mutually
                exclusive with folder/folders.
            resource_types: Limit search to these resource type names. Omit to search
                all types. Use scm_list_resource_types() to see valid values.
            exact_match: Match only objects whose name exactly equals query
                (case-sensitive). Default False (substring, case-insensitive).
            search_fields: Also match against field values — source, destination,
                application, service, zone fields, address values (ip_netmask, fqdn,
                ip_range), group members, URL list entries. Enables queries like
                "find all rules referencing 10.10.1.0/24". Default False.
            tags: Filter results to objects carrying ALL of these tags (applied at the
                list() level where the SDK supports it; falls back to client-side
                filtering for types that don't support server-side tag filtering).
            include_rulebases: For rule types, which rulebases to search.
                Default ['pre', 'post']. Pass ['pre'] or ['post'] to limit.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        rulebases = include_rulebases or ["pre", "post"]
        client = get_client(tsg_id)
        results: dict[str, list[dict]] = {}
        errors: dict[str, str] = {}
        target_labels = set(resource_types) if resource_types else None

        # Determine folder list to iterate over
        search_folders: list[str | None]
        if snippet:
            search_folders = [None]   # snippet scope, no folder iteration
        elif folders:
            search_folders = folders
        else:
            search_folders = [folder]

        for attr, needs_folder, is_rule, label in _RESOURCE_REGISTRY:
            if target_labels and label not in target_labels:
                continue

            resource = getattr(client, attr)
            seen_ids: set[str] = set()
            matches: list[dict] = []
            had_error = False

            folder_list = [None] if not needs_folder else search_folders
            rulebase_list = rulebases if is_rule else [None]

            for fold in folder_list:
                if had_error:
                    break
                for rb in rulebase_list:
                    try:
                        items = _list_resource(resource, needs_folder, is_rule,
                                               fold, snippet if needs_folder else None,
                                               rb, tags)
                        for item in items:
                            name = getattr(item, "name", None)
                            if not name:
                                continue
                            serialized = serialize(item)
                            obj_id = serialized.get("id") or name
                            if obj_id in seen_ids:
                                continue

                            name_hit = _name_matches(name, query, exact_match)
                            field_hit = search_fields and _fields_match(serialized, query)

                            if name_hit or field_hit:
                                seen_ids.add(obj_id)
                                if rb:
                                    serialized["_rulebase"] = rb
                                if fold and len(search_folders) > 1:
                                    serialized["_folder"] = fold
                                matches.append(serialized)
                    except Exception as exc:
                        errors[label] = str(exc)
                        had_error = True
                        break

            if matches:
                results[label] = matches

        return {
            "query": query,
            "folders_searched": search_folders if needs_folder else [],
            "snippet": snippet,
            "search_fields": search_fields,
            "tags_filter": tags,
            "results": results,
            "total_matches": sum(len(v) for v in results.values()),
            **({"errors": errors} if errors else {}),
        }

    @mcp.tool()
    def scm_list_resource_types() -> list[str]:
        """List all resource type names valid for use with scm_search.

        Returns the complete list of searchable resource type names that can be
        passed as the resource_types argument to scm_search.
        """
        return [label for _, _, _, label in _RESOURCE_REGISTRY]
