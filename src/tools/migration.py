"""Tools for cross-folder and cross-TSG migration: diff, copy, and clone operations."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize

# Metadata fields set by the server — stripped before re-creating an object elsewhere.
_META_FIELDS = {"id", "folder", "snippet", "device"}

# Copyable object types in dependency order.
# Types with dependencies come after the types they depend on so creates succeed.
# Entry: (accessor_attr, label)
_OBJECT_COPY_ORDER: list[tuple[str, str]] = [
    ("tag",                              "tags"),
    ("schedule",                         "schedules"),
    ("external_dynamic_list",            "external_dynamic_lists"),
    ("url_category",                     "url_categories"),
    ("address",                          "addresses"),
    ("address_group",                    "address_groups"),       # depends on addresses
    ("service",                          "services"),
    ("service_group",                    "service_groups"),       # depends on services
    ("application",                      "applications"),
    ("application_group",                "application_groups"),  # depends on applications
    ("application_filter",               "application_filters"),
    ("security_zone",                    "security_zones"),
    ("anti_spyware_profile",             "anti_spyware_profiles"),
    ("wildfire_antivirus_profile",       "wildfire_profiles"),
    ("vulnerability_protection_profile", "vulnerability_profiles"),
    ("dns_security_profile",             "dns_security_profiles"),
    ("decryption_profile",               "decryption_profiles"),
    ("url_access_profile",               "url_access_profiles"),
    ("file_blocking_profile",            "file_blocking_profiles"),
    ("zone_protection_profile",          "zone_protection_profiles"),
    ("log_forwarding_profile",           "log_forwarding_profiles"),
    ("http_server_profile",              "http_server_profiles"),
    ("syslog_server_profile",            "syslog_server_profiles"),
]

# Rule types with their rulebase/position kwarg name.
# Entry: (accessor_attr, label, rulebase_kwarg)
_RULE_COPY_ORDER: list[tuple[str, str, str]] = [
    ("security_rule",       "security_rules",       "rulebase"),
    ("nat_rule",            "nat_rules",            "position"),
    ("decryption_rule",     "decryption_rules",     "rulebase"),
    ("authentication_rule", "authentication_rules", "rulebase"),
    ("pbf_rule",            "pbf_rules",            "rulebase"),
    ("qos_rule",            "qos_rules",            "rulebase"),
]

_ALL_OBJECT_LABELS = {label for _, label in _OBJECT_COPY_ORDER}
_ALL_RULE_LABELS   = {label for _, label, _ in _RULE_COPY_ORDER}


def _strip_nulls(obj: any) -> any:
    """Recursively remove None values from dicts and lists."""
    if isinstance(obj, dict):
        return {k: _strip_nulls(v) for k, v in obj.items() if v is not None}
    if isinstance(obj, list):
        return [_strip_nulls(i) for i in obj]
    return obj


def _to_create_payload(obj: dict, dst_folder: str) -> dict:
    """Strip server-assigned metadata, remove nulls recursively, and set the destination folder."""
    payload = _strip_nulls({k: v for k, v in obj.items() if k not in _META_FIELDS})
    payload["folder"] = dst_folder
    return payload


def register(mcp: FastMCP) -> None:
    """Register migration tools on the given FastMCP instance."""

    @mcp.tool()
    def scm_diff_folders(
        src_folder: str,
        dst_folder: str,
        resource_types: list[str] | None = None,
        src_tsg_id: str | None = None,
        dst_tsg_id: str | None = None,
    ) -> dict:
        """Compare two folders (optionally across TSGs) and show what exists in each.

        For each resource type, returns three lists: objects only in the source,
        only in the destination, and present in both (compared by name).

        Args:
            src_folder: Source folder name (e.g. 'Texas').
            dst_folder: Destination folder name.
            resource_types: Limit to specific resource type labels. Defaults to all
                copyable object types. Valid values from scm_list_resource_types().
                Pass rule type labels (e.g. 'security_rules') to include rules.
            src_tsg_id: TSG for the source. Defaults to SCM_TSG_ID.
            dst_tsg_id: TSG for the destination. Defaults to src_tsg_id (same tenant,
                different folders). Pass a different value for cross-tenant diff.
        """
        src_client = get_client(src_tsg_id)
        dst_client = get_client(dst_tsg_id or src_tsg_id)
        target = set(resource_types) if resource_types else _ALL_OBJECT_LABELS
        results: dict[str, dict] = {}
        errors: dict[str, str] = {}

        # Build combined iteration list of (attr, label, rulebase_kwarg_or_None)
        all_types: list[tuple[str, str, str | None]] = []
        for attr, label in _OBJECT_COPY_ORDER:
            if label in target:
                all_types.append((attr, label, None))
        for attr, label, rb_kwarg in _RULE_COPY_ORDER:
            if label in target:
                all_types.append((attr, label, rb_kwarg))

        for attr, label, rb_kwarg in all_types:
            rulebases = ["pre", "post"] if rb_kwarg else [None]
            src_names: set[str] = set()
            dst_names: set[str] = set()

            for rb in rulebases:
                try:
                    src_kwargs: dict = {"folder": src_folder}
                    dst_kwargs: dict = {"folder": dst_folder}
                    if rb_kwarg and rb:
                        src_kwargs[rb_kwarg] = rb
                        dst_kwargs[rb_kwarg] = rb
                    src_names.update(
                        getattr(item, "name", None)
                        for item in getattr(src_client, attr).list(**src_kwargs)
                        if getattr(item, "name", None)
                    )
                    dst_names.update(
                        getattr(item, "name", None)
                        for item in getattr(dst_client, attr).list(**dst_kwargs)
                        if getattr(item, "name", None)
                    )
                except Exception as exc:
                    errors[label] = str(exc)
                    break

            if label not in errors:
                only_src = sorted(src_names - dst_names)
                only_dst = sorted(dst_names - src_names)
                in_both  = sorted(src_names & dst_names)
                if only_src or only_dst or in_both:
                    results[label] = {
                        "only_in_src": only_src,
                        "only_in_dst": only_dst,
                        "in_both": in_both,
                    }

        return {
            "src_folder": src_folder,
            "dst_folder": dst_folder,
            "results": results,
            **({"errors": errors} if errors else {}),
        }

    @mcp.tool()
    def scm_copy_objects(
        src_folder: str,
        dst_folder: str,
        resource_types: list[str] | None = None,
        src_tsg_id: str | None = None,
        dst_tsg_id: str | None = None,
        skip_existing: bool = True,
        dry_run: bool = False,
    ) -> dict:
        """Copy objects from one folder to another, optionally across TSGs.

        Objects are copied in dependency order (tags → addresses → address groups →
        services → service groups → ...) so that referenced objects exist in the
        destination before dependent objects are created.

        When skip_existing=True (default), objects whose name already exists in the
        destination are left untouched. Set skip_existing=False to raise an error on
        name collisions instead.

        Args:
            src_folder: Folder to copy objects from.
            dst_folder: Folder to copy objects into.
            resource_types: Limit to these resource type labels. Defaults to all
                non-rule object types. To include rules, pass their labels explicitly
                (e.g. ['security_rules', 'nat_rules']). Use scm_list_resource_types()
                for valid values.
            src_tsg_id: TSG for the source. Defaults to SCM_TSG_ID.
            dst_tsg_id: TSG for the destination. Defaults to src_tsg_id.
            skip_existing: Silently skip objects already present by name in the
                destination (default True). Set False to surface name collisions
                as errors instead.
            dry_run: Report what would be created without making any API calls
                (default False).
        """
        src_client = get_client(src_tsg_id)
        dst_client = get_client(dst_tsg_id or src_tsg_id)
        target = set(resource_types) if resource_types else _ALL_OBJECT_LABELS

        created: dict[str, list[str]] = {}
        skipped: dict[str, list[str]] = {}
        errors:  dict[str, list[str]] = {}

        # Build the ordered work list
        work: list[tuple[str, str, str | None]] = []
        for attr, label in _OBJECT_COPY_ORDER:
            if label in target:
                work.append((attr, label, None))
        for attr, label, rb_kwarg in _RULE_COPY_ORDER:
            if label in target:
                work.append((attr, label, rb_kwarg))

        for attr, label, rb_kwarg in work:
            rulebases = ["pre", "post"] if rb_kwarg else [None]
            src_resource = getattr(src_client, attr)
            dst_resource = getattr(dst_client, attr)

            # Build destination name set for collision detection
            dst_existing: set[str] = set()
            for rb in rulebases:
                try:
                    dst_kwargs: dict = {"folder": dst_folder}
                    if rb_kwarg and rb:
                        dst_kwargs[rb_kwarg] = rb
                    dst_existing.update(
                        getattr(item, "name", "")
                        for item in dst_resource.list(**dst_kwargs)
                    )
                except Exception as exc:
                    errors.setdefault(label, []).append(f"list dst error: {exc}")

            for rb in rulebases:
                try:
                    src_kwargs: dict = {"folder": src_folder}
                    if rb_kwarg and rb:
                        src_kwargs[rb_kwarg] = rb
                    src_items = src_resource.list(**src_kwargs)
                except Exception as exc:
                    errors.setdefault(label, []).append(f"list src error: {exc}")
                    continue

                for item in src_items:
                    name = getattr(item, "name", None)
                    if not name:
                        continue

                    if name in dst_existing:
                        if skip_existing:
                            skipped.setdefault(label, []).append(name)
                        else:
                            errors.setdefault(label, []).append(
                                f"{name}: already exists in destination"
                            )
                        continue

                    if dry_run:
                        created.setdefault(label, []).append(name)
                        dst_existing.add(name)  # prevent duplicate within this run
                        continue

                    try:
                        payload = _to_create_payload(serialize(item), dst_folder)
                        create_kwargs: dict = {}
                        if rb_kwarg and rb:
                            create_kwargs[rb_kwarg] = rb
                        dst_resource.create(payload, **create_kwargs)
                        created.setdefault(label, []).append(name)
                        dst_existing.add(name)
                    except Exception as exc:
                        errors.setdefault(label, []).append(f"{name}: {exc}")

        total_created = sum(len(v) for v in created.values())
        total_skipped = sum(len(v) for v in skipped.values())
        total_errors  = sum(len(v) for v in errors.values())

        return {
            "src_folder": src_folder,
            "dst_folder": dst_folder,
            "dry_run": dry_run,
            "summary": {
                "created": total_created,
                "skipped": total_skipped,
                "errors": total_errors,
            },
            "created": created,
            **({"skipped": skipped} if skipped else {}),
            **({"errors": errors} if errors else {}),
        }

    @mcp.tool()
    def scm_clone_security_rule(
        rule_id: str,
        dst_folder: str,
        dst_rulebase: str = "pre",
        new_name: str | None = None,
        src_tsg_id: str | None = None,
        dst_tsg_id: str | None = None,
    ) -> dict:
        """Clone a single security rule into a different folder or TSG.

        Fetches the rule by UUID, strips server-assigned metadata, and creates it
        in the destination. Referenced objects (addresses, applications, profiles)
        must already exist in the destination — this tool copies the rule only.

        Args:
            rule_id: UUID of the security rule to clone.
            dst_folder: Destination folder name.
            dst_rulebase: Destination rulebase — 'pre' (default) or 'post'.
            new_name: Override the rule name in the destination. If omitted, the
                original name is used. Useful when the name already exists.
            src_tsg_id: TSG to read the source rule from. Defaults to SCM_TSG_ID.
            dst_tsg_id: TSG to create the rule in. Defaults to src_tsg_id.
        """
        try:
            src_client = get_client(src_tsg_id)
            dst_client = get_client(dst_tsg_id or src_tsg_id)

            rule = src_client.security_rule.get(rule_id)
            payload = _to_create_payload(serialize(rule), dst_folder)

            if new_name:
                payload["name"] = new_name

            result = dst_client.security_rule.create(payload, rulebase=dst_rulebase)
            return serialize(result)
        except Exception as exc:
            return handle_error(exc)
