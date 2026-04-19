"""Tools for SCM security profiles: Anti-Spyware, WildFire Antivirus, Vulnerability Protection,
URL Access Profiles, URL Categories, DNS Security Profiles, Decryption Profiles,
File Blocking Profiles, Zone Protection Profiles."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all security profile tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # Anti-Spyware Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_anti_spyware_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List anti-spyware security profiles in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).anti_spyware_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_anti_spyware_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single anti-spyware profile by UUID.

        Args:
            profile_id: UUID of the anti-spyware profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).anti_spyware_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_anti_spyware_profile(
        name: str,
        folder: str,
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an anti-spyware security profile.

        Creates a profile with default settings. Use scm_update_anti_spyware_profile
        to add threat exception rules after creation.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            return serialize(get_client(tsg_id).anti_spyware_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_anti_spyware_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete an anti-spyware profile by UUID.

        Args:
            profile_id: UUID of the anti-spyware profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).anti_spyware_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # WildFire Antivirus Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_wildfire_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List WildFire antivirus profiles in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).wildfire_antivirus_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_wildfire_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single WildFire antivirus profile by UUID.

        Args:
            profile_id: UUID of the WildFire profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).wildfire_antivirus_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_wildfire_profile(
        name: str,
        folder: str,
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a WildFire antivirus security profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            return serialize(get_client(tsg_id).wildfire_antivirus_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_wildfire_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a WildFire antivirus profile by UUID.

        Args:
            profile_id: UUID of the WildFire profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).wildfire_antivirus_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Vulnerability Protection Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_vulnerability_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List vulnerability protection profiles in a folder.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).vulnerability_protection_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_vulnerability_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single vulnerability protection profile by UUID.

        Args:
            profile_id: UUID of the vulnerability protection profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).vulnerability_protection_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_vulnerability_profile(
        name: str,
        folder: str,
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a vulnerability protection security profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            return serialize(get_client(tsg_id).vulnerability_protection_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_vulnerability_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a vulnerability protection profile by UUID.

        Args:
            profile_id: UUID of the vulnerability protection profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).vulnerability_protection_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # URL Access Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_url_access_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List URL access (filtering) profiles in a folder.

        URL access profiles define what happens when users visit websites
        in specific URL categories — allow, block, alert, continue, or override.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).url_access_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_url_access_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single URL access profile by UUID.

        Args:
            profile_id: UUID of the URL access profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).url_access_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_url_access_profile(
        name: str,
        folder: str,
        description: str | None = None,
        allow_categories: list[str] | None = None,
        block_categories: list[str] | None = None,
        alert_categories: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a URL access (filtering) profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            allow_categories: URL categories to allow (optional).
            block_categories: URL categories to block (optional).
            alert_categories: URL categories to allow with alert (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            if allow_categories:
                data["allow_categories"] = allow_categories
            if block_categories:
                data["block_categories"] = block_categories
            if alert_categories:
                data["alert_categories"] = alert_categories
            return serialize(get_client(tsg_id).url_access_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_url_access_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a URL access profile by UUID.

        Args:
            profile_id: UUID of the URL access profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).url_access_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # URL Categories
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_url_categories(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List custom URL categories in a folder.

        Custom URL categories group specific URLs or domains for use in
        URL filtering profiles and security policies.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).url_category.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_url_category(category_id: str, tsg_id: str | None = None) -> dict:
        """Get a single custom URL category by UUID.

        Args:
            category_id: UUID of the URL category.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).url_category.get(category_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_url_category(
        name: str,
        folder: str,
        list_entries: list[str],
        category_type: str = "URL List",
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a custom URL category.

        Args:
            name: Unique name for the URL category.
            folder: Folder to create the category in.
            list_entries: List of URLs or domains to include (e.g. ['example.com', '*.evil.com']).
            category_type: Category type — 'URL List' (default) or 'Category Match'.
            description: Optional description.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "list": list_entries,
                "type": category_type,
            }
            if description:
                data["description"] = description
            return serialize(get_client(tsg_id).url_category.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_url_category(category_id: str, tsg_id: str | None = None) -> dict:
        """Delete a custom URL category by UUID.

        Args:
            category_id: UUID of the URL category to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).url_category.delete(category_id)
            return {"success": True, "deleted_id": category_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # DNS Security Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_dns_security_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List DNS security profiles in a folder.

        DNS security profiles control how the firewall responds to DNS queries
        for known malicious domains — block, sinkhole, or allow.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).dns_security_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_dns_security_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single DNS security profile by UUID.

        Args:
            profile_id: UUID of the DNS security profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).dns_security_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_dns_security_profile(
        name: str,
        folder: str,
        description: str | None = None,
        botnet_domains: dict | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a DNS security profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            botnet_domains: Optional botnet domain configuration dict. Controls
                threat categories and actions, e.g.:
                {'dns_security_categories': [{'name': 'pan-dns-sec-malware', 'action': 'sinkhole'}],
                 'sinkhole': {'ipv4_address': 'pan-sinkhole-default-ip'}}.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            if botnet_domains:
                data["botnet_domains"] = botnet_domains
            return serialize(get_client(tsg_id).dns_security_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_dns_security_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a DNS security profile by UUID.

        Args:
            profile_id: UUID of the DNS security profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).dns_security_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Decryption Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_decryption_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List decryption profiles in a folder.

        Decryption profiles control SSL/TLS inspection settings — protocol versions,
        cipher suites, and certificate validation behavior.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).decryption_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_decryption_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single decryption profile by UUID.

        Args:
            profile_id: UUID of the decryption profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).decryption_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_decryption_profile(
        name: str,
        folder: str,
        ssl_forward_proxy: dict | None = None,
        ssl_inbound_inspection: dict | None = None,
        ssl_no_proxy: dict | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a decryption profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            ssl_forward_proxy: Forward-proxy SSL inspection settings dict (optional).
                Keys include: block_expired_certificate, block_untrusted_issuer,
                block_unknown_cert, min_version ('tls1-0', 'tls1-1', 'tls1-2', 'tls1-3').
            ssl_inbound_inspection: Inbound inspection settings dict (optional).
                Keys: min_version, max_version.
            ssl_no_proxy: No-proxy settings dict for excluded traffic (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if ssl_forward_proxy:
                data["ssl_forward_proxy"] = ssl_forward_proxy
            if ssl_inbound_inspection:
                data["ssl_inbound_inspection"] = ssl_inbound_inspection
            if ssl_no_proxy:
                data["ssl_no_proxy"] = ssl_no_proxy
            return serialize(get_client(tsg_id).decryption_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_decryption_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a decryption profile by UUID.

        Args:
            profile_id: UUID of the decryption profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).decryption_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # File Blocking Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_file_blocking_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List file blocking profiles in a folder.

        File blocking profiles control which file types are allowed, blocked,
        or forwarded to WildFire for analysis.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).file_blocking_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_file_blocking_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single file blocking profile by UUID.

        Args:
            profile_id: UUID of the file blocking profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).file_blocking_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_file_blocking_profile(
        name: str,
        folder: str,
        description: str | None = None,
        rules: list[dict] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a file blocking profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            rules: Optional list of file blocking rules. Each rule dict includes:
                name, application (list), file_type (list), direction ('upload', 'download', 'both'),
                action ('alert', 'block', 'continue', 'forward').
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            if rules:
                data["rules"] = rules
            return serialize(get_client(tsg_id).file_blocking_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_file_blocking_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a file blocking profile by UUID.

        Args:
            profile_id: UUID of the file blocking profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).file_blocking_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Zone Protection Profiles
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_zone_protection_profiles(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List zone protection profiles in a folder.

        Zone protection profiles defend security zones against DoS/flood attacks,
        port scans, and other reconnaissance activity.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).zone_protection_profile.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_zone_protection_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Get a single zone protection profile by UUID.

        Args:
            profile_id: UUID of the zone protection profile.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).zone_protection_profile.get(profile_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_zone_protection_profile(
        name: str,
        folder: str,
        description: str | None = None,
        flood: dict | None = None,
        reconnaissance: dict | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a zone protection profile.

        Args:
            name: Unique name for the profile.
            folder: Folder to create the profile in.
            description: Optional description.
            flood: Flood protection settings dict (optional). Controls SYN, UDP, ICMP,
                and other flood thresholds, e.g.:
                {'syn': {'enable': True, 'red': {'alarm_rate': 10000, 'activate_rate': 10000}}}.
            reconnaissance: Reconnaissance protection settings dict (optional). Controls
                port scan and host sweep detection.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if description:
                data["description"] = description
            if flood:
                data["flood"] = flood
            if reconnaissance:
                data["reconnaissance"] = reconnaissance
            return serialize(get_client(tsg_id).zone_protection_profile.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_zone_protection_profile(profile_id: str, tsg_id: str | None = None) -> dict:
        """Delete a zone protection profile by UUID.

        Args:
            profile_id: UUID of the zone protection profile to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).zone_protection_profile.delete(profile_id)
            return {"success": True, "deleted_id": profile_id}
        except Exception as exc:
            return handle_error(exc)
