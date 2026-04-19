"""Tools for SCM policy objects: Addresses, Address Groups, Services, Service Groups, Tags,
Log Forwarding Profiles, HTTP Server Profiles, Syslog Server Profiles."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all object tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # Addresses
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_addresses(
        folder: str,
        name: str | None = None,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List address objects in a folder.

        Args:
            folder: Folder name to scope the query (e.g. 'All', 'Texas').
            name: Optional filter by address name (exact match).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            kwargs: dict = {"folder": folder}
            if name:
                kwargs["name"] = name
            return serialize(get_client(tsg_id).address.list(**kwargs))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_address(address_id: str, tsg_id: str | None = None) -> dict:
        """Get a single address object by UUID.

        Args:
            address_id: UUID of the address object.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).address.get(address_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_address(
        name: str,
        folder: str,
        ip_netmask: str | None = None,
        ip_range: str | None = None,
        ip_wildcard: str | None = None,
        fqdn: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an address object.

        Exactly one of ip_netmask, ip_range, ip_wildcard, or fqdn must be provided.

        Args:
            name: Unique name for the address object.
            folder: Folder to create the object in (e.g. 'Texas').
            ip_netmask: CIDR notation (e.g. '10.0.0.0/8' or '192.168.1.1/32').
            ip_range: IP range (e.g. '10.0.0.1-10.0.0.10').
            ip_wildcard: Wildcard mask (e.g. '10.20.1.0/0.0.248.255').
            fqdn: Fully qualified domain name (e.g. 'example.com').
            description: Optional description.
            tag: Optional list of tag names to apply.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if ip_netmask:
                data["ip_netmask"] = ip_netmask
            if ip_range:
                data["ip_range"] = ip_range
            if ip_wildcard:
                data["ip_wildcard"] = ip_wildcard
            if fqdn:
                data["fqdn"] = fqdn
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).address.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_address(
        address_id: str,
        name: str | None = None,
        ip_netmask: str | None = None,
        ip_range: str | None = None,
        ip_wildcard: str | None = None,
        fqdn: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing address object.

        Args:
            address_id: UUID of the address object to update.
            name: New name (optional).
            ip_netmask: New CIDR (optional).
            ip_range: New IP range (optional).
            ip_wildcard: New wildcard mask (optional).
            fqdn: New FQDN (optional).
            description: New description (optional).
            tag: New tag list (optional — replaces existing tags).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            addr = client.address.get(address_id)
            if name is not None:
                addr.name = name
            if ip_netmask is not None:
                addr.ip_netmask = ip_netmask
            if ip_range is not None:
                addr.ip_range = ip_range
            if ip_wildcard is not None:
                addr.ip_wildcard = ip_wildcard
            if fqdn is not None:
                addr.fqdn = fqdn
            if description is not None:
                addr.description = description
            if tag is not None:
                addr.tag = tag
            return serialize(client.address.update(addr))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_address(address_id: str, tsg_id: str | None = None) -> dict:
        """Delete an address object by UUID.

        Args:
            address_id: UUID of the address object to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).address.delete(address_id)
            return {"success": True, "deleted_id": address_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Address Groups
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_address_groups(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List address group objects in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).address_group.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_address_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Get a single address group by UUID.

        Args:
            group_id: UUID of the address group.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).address_group.get(group_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_address_group(
        name: str,
        folder: str,
        static: list[str] | None = None,
        dynamic_filter: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an address group.

        Provide either static (list of address object names) or dynamic_filter
        (a tag-based filter expression), not both.

        Args:
            name: Unique name for the address group.
            folder: Folder to create the group in.
            static: List of address object names for a static group.
            dynamic_filter: Tag-filter expression for a dynamic group (e.g. "'tag1' and 'tag2'").
            description: Optional description.
            tag: Optional list of tag names to apply to the group itself.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if static:
                data["static"] = static
            if dynamic_filter:
                data["dynamic"] = {"filter": dynamic_filter}
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).address_group.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_address_group(
        group_id: str,
        name: str | None = None,
        static: list[str] | None = None,
        dynamic_filter: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing address group.

        Args:
            group_id: UUID of the address group to update.
            name: New name (optional).
            static: New list of static addresses (optional).
            dynamic_filter: New dynamic filter expression (optional).
            description: New description (optional).
            tag: New tag list (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            grp = client.address_group.get(group_id)
            if name is not None:
                grp.name = name
            if static is not None:
                grp.static = static
            if dynamic_filter is not None:
                grp.dynamic = {"filter": dynamic_filter}
            if description is not None:
                grp.description = description
            if tag is not None:
                grp.tag = tag
            return serialize(client.address_group.update(grp))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_address_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Delete an address group by UUID.

        Args:
            group_id: UUID of the address group to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).address_group.delete(group_id)
            return {"success": True, "deleted_id": group_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Services
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_services(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List service objects in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).service.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_service(service_id: str, tsg_id: str | None = None) -> dict:
        """Get a single service object by UUID.

        Args:
            service_id: UUID of the service object.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).service.get(service_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_service(
        name: str,
        folder: str,
        protocol: str,
        destination_port: str,
        source_port: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a service object.

        Args:
            name: Unique name for the service.
            folder: Folder to create the service in.
            protocol: Transport protocol — 'tcp' or 'udp'.
            destination_port: Destination port(s), e.g. '80', '443', '8080-8090'.
            source_port: Optional source port(s).
            description: Optional description.
            tag: Optional list of tag names.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "protocol": {
                    protocol: {"port": destination_port}
                },
            }
            if source_port:
                data["protocol"][protocol]["source_port"] = source_port
            if description:
                data["description"] = description
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).service.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_service(
        service_id: str,
        name: str | None = None,
        description: str | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update a service object's name, description, or tags.

        To change the protocol or port, delete and recreate the service.

        Args:
            service_id: UUID of the service object to update.
            name: New name (optional).
            description: New description (optional).
            tag: New tag list (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            svc = client.service.get(service_id)
            if name is not None:
                svc.name = name
            if description is not None:
                svc.description = description
            if tag is not None:
                svc.tag = tag
            return serialize(client.service.update(svc))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_service(service_id: str, tsg_id: str | None = None) -> dict:
        """Delete a service object by UUID.

        Args:
            service_id: UUID of the service object to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).service.delete(service_id)
            return {"success": True, "deleted_id": service_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Service Groups
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_service_groups(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List service group objects in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).service_group.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_service_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Get a single service group by UUID.

        Args:
            group_id: UUID of the service group.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).service_group.get(group_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_service_group(
        name: str,
        folder: str,
        members: list[str],
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a service group.

        Args:
            name: Unique name for the service group.
            folder: Folder to create the group in.
            members: List of service object names to include.
            tag: Optional list of tag names.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder, "members": members}
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).service_group.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_service_group(
        group_id: str,
        name: str | None = None,
        members: list[str] | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update a service group.

        Args:
            group_id: UUID of the service group to update.
            name: New name (optional).
            members: New members list (optional — replaces existing members).
            tag: New tag list (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            grp = client.service_group.get(group_id)
            if name is not None:
                grp.name = name
            if members is not None:
                grp.members = members
            if tag is not None:
                grp.tag = tag
            return serialize(client.service_group.update(grp))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_service_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Delete a service group by UUID.

        Args:
            group_id: UUID of the service group to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).service_group.delete(group_id)
            return {"success": True, "deleted_id": group_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_tags(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List tags in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).tag.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_tag(tag_id: str, tsg_id: str | None = None) -> dict:
        """Get a single tag by UUID.

        Args:
            tag_id: UUID of the tag.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).tag.get(tag_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_tag(
        name: str,
        folder: str,
        color: str | None = None,
        comments: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a tag.

        Args:
            name: Unique name for the tag.
            folder: Folder to create the tag in.
            color: Optional color name (e.g. 'Red', 'Blue', 'Green').
            comments: Optional description/comments.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if color:
                data["color"] = color
            if comments:
                data["comments"] = comments
            return serialize(get_client(tsg_id).tag.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_tag(
        tag_id: str,
        name: str | None = None,
        color: str | None = None,
        comments: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing tag.

        Args:
            tag_id: UUID of the tag to update.
            name: New name (optional).
            color: New color (optional).
            comments: New comments (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            tag = client.tag.get(tag_id)
            if name is not None:
                tag.name = name
            if color is not None:
                tag.color = color
            if comments is not None:
                tag.comments = comments
            return serialize(client.tag.update(tag))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_tag(tag_id: str, tsg_id: str | None = None) -> dict:
        """Delete a tag by UUID.

        Args:
            tag_id: UUID of the tag to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).tag.delete(tag_id)
            return {"success": True, "deleted_id": tag_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Log Forwarding Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_log_forwarding_profiles(
        folder: str,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List log forwarding profiles in a folder.

        Log forwarding profiles define where firewall logs (traffic, threat, etc.)
        are sent — e.g. to Panorama, syslog, or HTTP servers.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).log_forwarding_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_log_forwarding_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Get a single log forwarding profile by UUID.

        Args:
            profile_id: UUID of the log forwarding profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).log_forwarding_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_log_forwarding_profile(
        name: str,
        folder: str,
        description: str | None = None,
        enhanced_logging: bool = False,
        match_list: list[dict] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a log forwarding profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            enhanced_logging: Enable enhanced application logging (default False).
            match_list: Optional list of match list entries defining log destinations.
                Each entry is a dict with keys like: name, log_type, filter, send_syslog,
                send_http, send_email.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            if enhanced_logging:
                data["enhanced_logging"] = enhanced_logging
            if match_list:
                data["match_list"] = match_list
            return serialize(get_client(tsg_id).log_forwarding_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_log_forwarding_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Delete a log forwarding profile by UUID.

        Args:
            profile_id: UUID of the log forwarding profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).log_forwarding_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # HTTP Server Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_http_server_profiles(
        folder: str,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List HTTP server profiles in a folder.

        HTTP server profiles define HTTP endpoints that receive log data from
        log forwarding profiles.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).http_server_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_http_server_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Get a single HTTP server profile by UUID.

        Args:
            profile_id: UUID of the HTTP server profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).http_server_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_http_server_profile(
        name: str,
        folder: str,
        server: list[dict],
        description: str | None = None,
        tag_registration: bool = False,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an HTTP server profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            server: List of server definitions. Each dict requires: name, address, protocol
                ('HTTP' or 'HTTPS'), port (default 443), and optionally http_method
                ('POST' or 'PUT'), tls_version, certificate_profile.
            description: Optional description.
            tag_registration: Enable tag registration via HTTP (default False).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder, "server": server}
            if description:
                data["description"] = description
            if tag_registration:
                data["tag_registration"] = tag_registration
            return serialize(get_client(tsg_id).http_server_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_http_server_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Delete an HTTP server profile by UUID.

        Args:
            profile_id: UUID of the HTTP server profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).http_server_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Syslog Server Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_syslog_server_profiles(
        folder: str,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List syslog server profiles in a folder.

        Syslog server profiles define syslog endpoints for log forwarding.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).syslog_server_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_syslog_server_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Get a single syslog server profile by UUID.

        Args:
            profile_id: UUID of the syslog server profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).syslog_server_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_syslog_server_profile(
        name: str,
        folder: str,
        server: list[dict],
        tsg_id: str | None = None,
    ) -> dict:
        """Create a syslog server profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            server: List of syslog server definitions. Each dict requires: name, server
                (hostname/IP), and optionally transport ('UDP', 'TCP', 'SSL'), port
                (default 514), format ('BSD' or 'IETF'), facility.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder, "server": server}
            return serialize(get_client(tsg_id).syslog_server_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_syslog_server_profile(
        profile_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Delete a syslog server profile by UUID.

        Args:
            profile_id: UUID of the syslog server profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).syslog_server_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)
