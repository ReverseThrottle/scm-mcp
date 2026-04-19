"""Tools for SCM network configuration: NAT Rules, PBF Rules, QoS Rules."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all network tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # NAT Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_nat_rules(
        folder: str,
        position: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List NAT rules in a folder.

        Args:
            folder: Folder name to scope the query.
            position: Rule position — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).nat_rule.list(folder=folder, position=position))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_nat_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single NAT rule by UUID.

        Args:
            rule_id: UUID of the NAT rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).nat_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_nat_rule(
        name: str,
        folder: str,
        nat_type: str,
        source_zone: list[str],
        destination_zone: list[str],
        source: list[str] | None = None,
        destination: list[str] | None = None,
        service: str | None = None,
        source_translation: dict | None = None,
        destination_translation: dict | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a NAT rule.

        Args:
            name: Unique name for the NAT rule.
            folder: Folder to create the rule in.
            nat_type: NAT type — 'ipv4' (most common), 'nat64', or 'nptv6'.
            source_zone: List of source zone names.
            destination_zone: List of destination zone names.
            source: Source address objects/groups (default ['any']).
            destination: Destination address objects/groups (default ['any']).
            service: Service name (default 'any').
            source_translation: Dict describing source NAT, e.g.
                {'dynamic_ip_and_port': {'interface_address': {'interface': 'ethernet1/1'}}}.
            destination_translation: Dict describing destination NAT (DNAT/port forwarding), e.g.
                {'translated_address': '10.0.0.5', 'translated_port': 8080}.
            description: Optional description.
            tag: Optional list of tag names.
            disabled: Whether the rule is disabled (default False).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "nat_type": nat_type,
                "from": source_zone,
                "to": destination_zone,
                "source": source or ["any"],
                "destination": destination or ["any"],
                "service": service or "any",
                "disabled": disabled,
            }
            if source_translation:
                data["source_translation"] = source_translation
            if destination_translation:
                data["destination_translation"] = destination_translation
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).nat_rule.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_nat_rule(
        rule_id: str,
        name: str | None = None,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        service: str | None = None,
        source_translation: dict | None = None,
        destination_translation: dict | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing NAT rule.

        Args:
            rule_id: UUID of the NAT rule to update.
            name: New name (optional).
            source_zone: New source zones (optional).
            destination_zone: New destination zones (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            service: New service (optional).
            source_translation: New source translation config (optional).
            destination_translation: New destination translation config (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.nat_rule.get(rule_id)
            if name is not None:
                rule.name = name
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
            if source_translation is not None:
                rule.source_translation = source_translation
            if destination_translation is not None:
                rule.destination_translation = destination_translation
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.nat_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_nat_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a NAT rule by UUID.

        Args:
            rule_id: UUID of the NAT rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).nat_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Policy-Based Forwarding (PBF) Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_pbf_rules(
        folder: str,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List policy-based forwarding (PBF) rules in a folder.

        PBF rules override routing table decisions — useful for directing specific
        traffic through a different egress interface or next-hop.

        Args:
            folder: Folder name to scope the query.
            rulebase: Which rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).pbf_rule.list(folder=folder, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_pbf_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single PBF rule by UUID.

        Args:
            rule_id: UUID of the PBF rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).pbf_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_pbf_rule(
        name: str,
        folder: str,
        source_zone: list[str],
        action: dict,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> dict:
        """Create a policy-based forwarding rule.

        Args:
            name: Unique name for the PBF rule.
            folder: Folder to create the rule in.
            source_zone: List of source zone names.
            action: Forwarding action dict. For nexthop forwarding:
                {'forward': {'nexthop': {'ip_address': '10.0.0.1'}}}.
                For discard: {'discard': {}}.
                For no-pbf (fall back to routing): {'no_pbf': {}}.
            source: Source address objects/groups (default ['any']).
            destination: Destination address objects/groups (default ['any']).
            application: Application names (default ['any']).
            service: Service names (default ['any']).
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
                "source": source or ["any"],
                "destination": destination or ["any"],
                "application": application or ["any"],
                "service": service or ["any"],
                "action": action,
                "disabled": disabled,
            }
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).pbf_rule.create(data, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_pbf_rule(
        rule_id: str,
        name: str | None = None,
        source_zone: list[str] | None = None,
        action: dict | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing PBF rule.

        Args:
            rule_id: UUID of the PBF rule to update.
            name: New name (optional).
            source_zone: New source zones (optional).
            action: New forwarding action dict (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            application: New applications (optional).
            service: New services (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.pbf_rule.get(rule_id)
            if name is not None:
                rule.name = name
            if source_zone is not None:
                rule.from_ = source_zone
            if action is not None:
                rule.action = action
            if source is not None:
                rule.source = source
            if destination is not None:
                rule.destination = destination
            if application is not None:
                rule.application = application
            if service is not None:
                rule.service = service
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.pbf_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_pbf_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a PBF rule by UUID.

        Args:
            rule_id: UUID of the PBF rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).pbf_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # QoS Rules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_qos_rules(
        folder: str,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List QoS policy rules in a folder.

        QoS rules classify and mark traffic for bandwidth management and
        quality-of-service enforcement.

        Args:
            folder: Folder name to scope the query.
            rulebase: Which rulebase — 'pre' (default) or 'post'.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).qos_rule.list(folder=folder, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_qos_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single QoS rule by UUID.

        Args:
            rule_id: UUID of the QoS rule.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).qos_rule.get(rule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_qos_rule(
        name: str,
        folder: str,
        action: dict,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool = False,
        rulebase: str = "pre",
        tsg_id: str | None = None,
    ) -> dict:
        """Create a QoS policy rule.

        Args:
            name: Unique name for the QoS rule.
            folder: Folder to create the rule in.
            action: QoS action dict, e.g. {'class': '4'} to assign to QoS class 4.
            source_zone: Source zone names (default ['any']).
            destination_zone: Destination zone names (default ['any']).
            source: Source address objects/groups (default ['any']).
            destination: Destination address objects/groups (default ['any']).
            application: Application names (default ['any']).
            service: Service names (default ['any']).
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
                "from": source_zone or ["any"],
                "to": destination_zone or ["any"],
                "source": source or ["any"],
                "destination": destination or ["any"],
                "application": application or ["any"],
                "service": service or ["any"],
                "action": action,
                "disabled": disabled,
            }
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).qos_rule.create(data, rulebase=rulebase))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_qos_rule(
        rule_id: str,
        name: str | None = None,
        action: dict | None = None,
        source_zone: list[str] | None = None,
        destination_zone: list[str] | None = None,
        source: list[str] | None = None,
        destination: list[str] | None = None,
        application: list[str] | None = None,
        service: list[str] | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        disabled: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing QoS rule.

        Args:
            rule_id: UUID of the QoS rule to update.
            name: New name (optional).
            action: New QoS action dict (optional).
            source_zone: New source zones (optional).
            destination_zone: New destination zones (optional).
            source: New source addresses (optional).
            destination: New destination addresses (optional).
            application: New applications (optional).
            service: New services (optional).
            description: New description (optional).
            tag: New tag list (optional).
            disabled: New disabled state (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            rule = client.qos_rule.get(rule_id)
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
            if description is not None:
                rule.description = description
            if tag is not None:
                rule.tag = tag
            if disabled is not None:
                rule.disabled = disabled
            return serialize(client.qos_rule.update(rule))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_qos_rule(rule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a QoS rule by UUID.

        Args:
            rule_id: UUID of the QoS rule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).qos_rule.delete(rule_id)
            return {"success": True, "deleted_id": rule_id}
        except Exception as exc:
            return handle_error(exc)
