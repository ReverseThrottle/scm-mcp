"""Tools for SCM security configuration: Security Rules, Security Zones,
Decryption Rules, Authentication Rules."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all security tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # Security Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_security_rules(
        folder: str,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List security policy rules in a folder.

        Args:
            folder: Folder name to scope the query (e.g. 'All', 'Texas').
            rulebase: Which rulebase to query — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).security_rule.list(folder=folder, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_security_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single security rule by UUID.

        Args:
            rule_id: UUID of the security rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).security_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_security_rule(
        name: str,
        folder: str,
        action: str,
        source_zone: list[str],
        destination_zone: list[str],
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        profile_setting: dict | None = None,
        log_setting: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> dict:
        """Create a security policy rule.

        Args:
            name: Unique name for the rule.
            folder: Folder to create the rule in.
            action: Rule action — 'allow' or 'deny'.
            source_zone: List of source zone names (e.g. ['trust', 'any']).
            destination_zone: List of destination zone names.
            source: List of source address objects/groups (default ['any']).
            destination: List of destination address objects/groups (default ['any']).
            application: List of application names (default ['any']).
            service: List of service names (default ['application-default']).
            profile_setting: Optional security profile group dict,
                e.g. {'group': ['best-practice']}.
            log_setting: Optional log forwarding profile name.
            description: Optional description.
            tag: Optional list of tag names.
            disabled: Whether the rule is disabled (default False).
            rulebase: Which rulebase to add the rule to — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "action": action,
                "from": source_zone,
                "to": destination_zone,
                "source": source or ["any"],
                "destination": destination or ["any"],
                "application": application or ["any"],
                "service": service or ["application-default"],
                "disabled": disabled,
            }
            if profile_setting:
                data["profile_setting"] = profile_setting
            if log_setting:
                data["log_setting"] = log_setting
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).security_rule.create(data, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_security_rule(
        rule_id: str,
        name: str | None = None,
        action: str | None = None,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        profile_setting: dict | None = None,
        log_setting: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing security rule.

        Args:
            rule_id: UUID of the security rule to update.
            name: New name (optional).
            action: New action — 'allow' or 'deny' (optional).
            source_zone: New source zones (optional).
            destination_zone: New destination zones (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            application: New applications (optional).
            service: New services (optional).
            profile_setting: New profile setting dict (optional).
            log_setting: New log forwarding profile (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.security_rule.get(rule_id)
            if name is not None:
                rule.name = name
            if action is not None:
                rule.action = action
            if source_zone is not None:
                rule.from_ = source_zone
            if destination_zone is not None:
                rule.to = destination_zone
            if source is not None:
                rule.source = source
            if destination is not None:
                rule.destination = destination
            if application is not None:
                rule.application = application
            if service is not None:
                rule.service = service
            if profile_setting is not None:
                rule.profile_setting = profile_setting
            if log_setting is not None:
                rule.log_setting = log_setting
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.security_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_security_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a security rule by UUID.

        Args:
            rule_id: UUID of the security rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).security_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_move_security_rule(
        rule_id: str,
        destination: str,
        folder: str,
        destination_rule: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Move a security rule to a different position in the rulebase.

        Args:
            rule_id: UUID of the rule to move.
            destination: Where to move the rule — 'top', 'bottom', 'before', or 'after'.
            folder: Folder context for the move operation.
            destination_rule: UUID of the pivot rule (required when destination
                is 'before' or 'after').
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            move_cfg: dict = {"destination": destination}
            if destination_rule:
                move_cfg["destination_rule"] = destination_rule
            get_client(tsg_id).security_rule.move(rule_id, move_cfg)
            return {"success": True, "rule_id": rule_id, "destination": destination}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Security Zones
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_security_zones(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List security zones in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).security_zone.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_security_zone(zone_id: str, tsg_id: str | None = None) -> dict:
        """Get a single security zone by UUID.

        Args:
            zone_id: UUID of the security zone.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).security_zone.get(zone_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_security_zone(
        name: str,
        folder: str,
        enable_user_id: bool = False,
        dos_profile: str | None = None,
        dos_log_setting: str | None = None,
        network_layer3: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a security zone.

        Args:
            name: Unique name for the zone.
            folder: Folder to create the zone in.
            enable_user_id: Enable User-ID for this zone (default False).
            dos_profile: Optional DoS protection profile name.
            dos_log_setting: Optional DoS log forwarding profile name.
            network_layer3: Optional list of Layer 3 interface names to add.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "enable_user_identification": enable_user_id,
            }
            if dos_profile:
                data["dos_profile"] = dos_profile
            if dos_log_setting:
                data["dos_log_setting"] = dos_log_setting
            if network_layer3:
                data["network"] = {"layer3": network_layer3}
            return serialize(get_client(tsg_id).security_zone.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_security_zone(
        zone_id: str,
        name: str | None = None,
        enable_user_id: bool | None = None,
        dos_profile: str | None = None,
        network_layer3: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing security zone.

        Args:
            zone_id: UUID of the security zone to update.
            name: New name (optional).
            enable_user_id: New User-ID enabled state (optional).
            dos_profile: New DoS protection profile name (optional).
            network_layer3: New list of Layer 3 interfaces (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            zone = client.security_zone.get(zone_id)
            if name is not None:
                zone.name = name
            if enable_user_id is not None:
                zone.enable_user_identification = enable_user_id
            if dos_profile is not None:
                zone.dos_profile = dos_profile
            if network_layer3 is not None:
                zone.network = {"layer3": network_layer3}
            return serialize(client.security_zone.update(zone))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_security_zone(zone_id: str, tsg_id: str | None = None) -> dict:
        """Delete a security zone by UUID.

        Args:
            zone_id: UUID of the security zone to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).security_zone.delete(zone_id)
            return {"success": True, "deleted_id": zone_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Decryption Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_decryption_rules(
        folder: str,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List decryption policy rules in a folder.

        Decryption rules control SSL/TLS traffic inspection — which sessions are
        decrypted, forwarded, or excluded from decryption.

        Args:
            folder: Folder name to scope the query.
            rulebase: Which rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).decryption_rule.list(folder=folder, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_decryption_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single decryption rule by UUID.

        Args:
            rule_id: UUID of the decryption rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).decryption_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_decryption_rule(
        name: str,
        folder: str,
        action: str,
        source_zone: list[str],
        destination_zone: list[str],
        source: list[str] | None = None,
        destination: list[str] | None = None,
        service: list[str] | None = None,
        profile: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> dict:
        """Create a decryption policy rule.

        Args:
            name: Unique name for the rule.
            folder: Folder to create the rule in.
            action: Decryption action — 'decrypt', 'no-decrypt'.
            source_zone: List of source zone names.
            destination_zone: List of destination zone names.
            source: Source address objects/groups (default ['any']).
            destination: Destination address objects/groups (default ['any']).
            service: List of service names (default ['any']).
            profile: Decryption profile name to apply (optional).
            description: Optional description.
            tag: Optional list of tag names.
            disabled: Whether the rule is disabled (default False).
            rulebase: Rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "action": action,
                "from": source_zone,
                "to": destination_zone,
                "source": source or ["any"],
                "destination": destination or ["any"],
                "service": service or ["any"],
                "disabled": disabled,
            }
            if profile:
                data["profile"] = profile
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).decryption_rule.create(data, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_decryption_rule(
        rule_id: str,
        name: str | None = None,
        action: str | None = None,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        service: list[str] | None = None,
        profile: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing decryption rule.

        Args:
            rule_id: UUID of the decryption rule to update.
            name: New name (optional).
            action: New action (optional).
            source_zone: New source zones (optional).
            destination_zone: New destination zones (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            service: New services (optional).
            profile: New decryption profile (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.decryption_rule.get(rule_id)
            if name is not None:
                rule.name = name
            if action is not None:
                rule.action = action
            if source_zone is not None:
                rule.from_ = source_zone
            if destination_zone is not None:
                rule.to = destination_zone
            if source is not None:
                rule.source = source
            if destination is not None:
                rule.destination = destination
            if service is not None:
                rule.service = service
            if profile is not None:
                rule.profile = profile
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.decryption_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_decryption_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a decryption rule by UUID.

        Args:
            rule_id: UUID of the decryption rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).decryption_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Authentication Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_authentication_rules(
        folder: str,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List authentication policy rules in a folder.

        Authentication rules enforce user identity verification before allowing
        access — typically used with Captive Portal or MFA.

        Args:
            folder: Folder name to scope the query.
            rulebase: Which rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).authentication_rule.list(folder=folder, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_authentication_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single authentication rule by UUID.

        Args:
            rule_id: UUID of the authentication rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).authentication_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_authentication_rule(
        name: str,
        folder: str,
        source_zone: list[str],
        destination_zone: list[str],
        authentication_enforcement: str,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        source_user: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> dict:
        """Create an authentication policy rule.

        Args:
            name: Unique name for the rule.
            folder: Folder to create the rule in.
            source_zone: List of source zone names.
            destination_zone: List of destination zone names.
            authentication_enforcement: Authentication enforcement profile name.
            source: Source address objects/groups (default ['any']).
            destination: Destination address objects/groups (default ['any']).
            source_user: Source user/group names (default ['any']).
            description: Optional description.
            tag: Optional list of tag names.
            disabled: Whether the rule is disabled (default False).
            rulebase: Rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "from": source_zone,
                "to": destination_zone,
                "source": source or ["any"],
                "destination": destination or ["any"],
                "source_user": source_user or ["any"],
                "authentication_enforcement": authentication_enforcement,
                "disabled": disabled,
            }
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).authentication_rule.create(data, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_authentication_rule(
        rule_id: str,
        name: str | None = None,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        authentication_enforcement: str | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        source_user: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing authentication rule.

        Args:
            rule_id: UUID of the authentication rule to update.
            name: New name (optional).
            source_zone: New source zones (optional).
            destination_zone: New destination zones (optional).
            authentication_enforcement: New enforcement profile (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            source_user: New source users/groups (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.authentication_rule.get(rule_id)
            if name is not None:
                rule.name = name
            if source_zone is not None:
                rule.from_ = source_zone
            if destination_zone is not None:
                rule.to = destination_zone
            if authentication_enforcement is not None:
                rule.authentication_enforcement = authentication_enforcement
            if source is not None:
                rule.source = source
            if destination is not None:
                rule.destination = destination
            if source_user is not None:
                rule.source_user = source_user
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.authentication_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_authentication_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete an authentication rule by UUID.

        Args:
            rule_id: UUID of the authentication rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).authentication_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)
