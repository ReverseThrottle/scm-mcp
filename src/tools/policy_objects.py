"""Tools for SCM policy objects: Applications, Application Groups, Application Filters,
Schedules, External Dynamic Lists."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all policy object tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # Applications
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_applications(
        folder: str,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List application objects in a folder.

        Applications are the building blocks of application-based security policy.
        This returns both predefined and custom application objects.

        Args:
            folder: Folder name to scope the query (e.g. 'All', 'Predefined').
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_application(app_id: str, tsg_id: str | None = None) -> dict:
        """Get a single application object by UUID.

        Args:
            app_id: UUID of the application object.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application.get(app_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_application(
        name: str,
        folder: str,
        category: str,
        subcategory: str,
        technology: str,
        risk: int,
        description: str | None = None,
        ports: list[str] | None = None,
        evasive: bool = False,
        pervasive: bool = False,
        excessive_bandwidth: bool = False,
        used_by_malware: bool = False,
        transfers_files: bool = False,
        has_known_vulnerabilities: bool = False,
        tunnels_other_apps: bool = False,
        prone_to_misuse: bool = False,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a custom application object.

        Args:
            name: Unique name for the application.
            folder: Folder to create the application in.
            category: Application category (e.g. 'business-systems', 'collaboration').
            subcategory: Application subcategory (e.g. 'database', 'email').
            technology: Underlying technology (e.g. 'client-server', 'peer-to-peer').
            risk: Risk level 1-5 (1=low, 5=critical).
            description: Optional description.
            ports: Optional list of port/protocol entries (e.g. ['tcp/80', 'udp/53']).
            evasive: Application uses evasion techniques (default False).
            pervasive: Application is widely used (default False).
            excessive_bandwidth: Consumes excessive bandwidth (default False).
            used_by_malware: Known to be used by malware (default False).
            transfers_files: Capable of file transfer (default False).
            has_known_vulnerabilities: Has known CVEs (default False).
            tunnels_other_apps: Can tunnel other applications (default False).
            prone_to_misuse: Prone to misuse (default False).
            tag: Optional list of tag names.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "category": category,
                "subcategory": subcategory,
                "technology": technology,
                "risk": risk,
            }
            if description:
                data["description"] = description
            if ports:
                data["ports"] = ports
            if evasive:
                data["evasive"] = evasive
            if pervasive:
                data["pervasive"] = pervasive
            if excessive_bandwidth:
                data["excessive_bandwidth_use"] = excessive_bandwidth
            if used_by_malware:
                data["used_by_malware"] = used_by_malware
            if transfers_files:
                data["able_to_transfer_file"] = transfers_files
            if has_known_vulnerabilities:
                data["has_known_vulnerabilities"] = has_known_vulnerabilities
            if tunnels_other_apps:
                data["tunnel_other_application"] = tunnels_other_apps
            if prone_to_misuse:
                data["prone_to_misuse"] = prone_to_misuse
            if tag:
                data["tag"] = tag
            return serialize(get_client(tsg_id).application.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_application(
        app_id: str,
        name: str | None = None,
        description: str | None = None,
        risk: int | None = None,
        ports: list[str] | None = None,
        tag: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update a custom application object.

        Args:
            app_id: UUID of the application to update.
            name: New name (optional).
            description: New description (optional).
            risk: New risk level 1-5 (optional).
            ports: New port list (optional — replaces existing).
            tag: New tag list (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            app = client.application.get(app_id)
            if name is not None:
                app.name = name
            if description is not None:
                app.description = description
            if risk is not None:
                app.risk = risk
            if ports is not None:
                app.ports = ports
            if tag is not None:
                app.tag = tag
            return serialize(client.application.update(app))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_application(app_id: str, tsg_id: str | None = None) -> dict:
        """Delete a custom application object by UUID.

        Args:
            app_id: UUID of the application to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).application.delete(app_id)
            return {"success": True, "deleted_id": app_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Application Groups
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_application_groups(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List application group objects in a folder.

        Application groups bundle multiple applications for use in security policy.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application_group.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_application_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Get a single application group by UUID.

        Args:
            group_id: UUID of the application group.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application_group.get(group_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_application_group(
        name: str,
        folder: str,
        members: list[str],
        tsg_id: str | None = None,
    ) -> dict:
        """Create an application group.

        Args:
            name: Unique name for the application group.
            folder: Folder to create the group in.
            members: List of application names to include.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder, "members": members}
            return serialize(get_client(tsg_id).application_group.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_application_group(
        group_id: str,
        name: str | None = None,
        members: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an application group.

        Args:
            group_id: UUID of the application group to update.
            name: New name (optional).
            members: New members list (optional — replaces existing).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            grp = client.application_group.get(group_id)
            if name is not None:
                grp.name = name
            if members is not None:
                grp.members = members
            return serialize(client.application_group.update(grp))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_application_group(group_id: str, tsg_id: str | None = None) -> dict:
        """Delete an application group by UUID.

        Args:
            group_id: UUID of the application group to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).application_group.delete(group_id)
            return {"success": True, "deleted_id": group_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Application Filters
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_application_filters(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List application filter objects in a folder.

        Application filters dynamically match applications based on attributes
        (category, subcategory, technology, risk) for use in security policy.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application_filter.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_application_filter(filter_id: str, tsg_id: str | None = None) -> dict:
        """Get a single application filter by UUID.

        Args:
            filter_id: UUID of the application filter.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).application_filter.get(filter_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_application_filter(
        name: str,
        folder: str,
        category: list[str] | None = None,
        subcategory: list[str] | None = None,
        technology: list[str] | None = None,
        risk: list[int] | None = None,
        evasive: bool | None = None,
        used_by_malware: bool | None = None,
        transfers_files: bool | None = None,
        has_known_vulnerabilities: bool | None = None,
        tunnels_other_apps: bool | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an application filter.

        Filters match applications dynamically by their attributes. At least one
        filter criterion should be specified.

        Args:
            name: Unique name for the filter.
            folder: Folder to create the filter in.
            category: Match applications in these categories (optional).
            subcategory: Match applications in these subcategories (optional).
            technology: Match applications using these technologies (optional).
            risk: Match applications with these risk levels 1-5 (optional).
            evasive: Match evasive applications (optional).
            used_by_malware: Match applications used by malware (optional).
            transfers_files: Match applications that transfer files (optional).
            has_known_vulnerabilities: Match apps with known CVEs (optional).
            tunnels_other_apps: Match apps that tunnel other apps (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder}
            if category:
                data["category"] = category
            if subcategory:
                data["subcategory"] = subcategory
            if technology:
                data["technology"] = technology
            if risk:
                data["risk"] = risk
            if evasive is not None:
                data["evasive"] = evasive
            if used_by_malware is not None:
                data["used_by_malware"] = used_by_malware
            if transfers_files is not None:
                data["able_to_transfer_file"] = transfers_files
            if has_known_vulnerabilities is not None:
                data["has_known_vulnerabilities"] = has_known_vulnerabilities
            if tunnels_other_apps is not None:
                data["tunnel_other_application"] = tunnels_other_apps
            return serialize(get_client(tsg_id).application_filter.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_application_filter(filter_id: str, tsg_id: str | None = None) -> dict:
        """Delete an application filter by UUID.

        Args:
            filter_id: UUID of the application filter to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).application_filter.delete(filter_id)
            return {"success": True, "deleted_id": filter_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Schedules
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_schedules(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List schedule objects in a folder.

        Schedules define time windows for use in security policy — recurring
        (weekly) or non-recurring (one-time) time ranges.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).schedule.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_schedule(schedule_id: str, tsg_id: str | None = None) -> dict:
        """Get a single schedule object by UUID.

        Args:
            schedule_id: UUID of the schedule object.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).schedule.get(schedule_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_schedule(
        name: str,
        folder: str,
        schedule_type: dict,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a schedule object.

        Args:
            name: Unique name for the schedule.
            folder: Folder to create the schedule in.
            schedule_type: Schedule definition dict. For recurring weekly schedule:
                {'recurring': {'weekly': {'monday': ['09:00-17:00'], 'tuesday': ['09:00-17:00']}}}.
                For non-recurring (one-time) schedule:
                {'non_recurring': ['2026-01-01T09:00:00/2026-01-01T17:00:00']}.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {
                "name": name,
                "folder": folder,
                "schedule_type": schedule_type,
            }
            return serialize(get_client(tsg_id).schedule.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_schedule(
        schedule_id: str,
        name: str | None = None,
        schedule_type: dict | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing schedule object.

        Args:
            schedule_id: UUID of the schedule to update.
            name: New name (optional).
            schedule_type: New schedule definition dict (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            sched = client.schedule.get(schedule_id)
            if name is not None:
                sched.name = name
            if schedule_type is not None:
                sched.schedule_type = schedule_type
            return serialize(client.schedule.update(sched))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_schedule(schedule_id: str, tsg_id: str | None = None) -> dict:
        """Delete a schedule object by UUID.

        Args:
            schedule_id: UUID of the schedule to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).schedule.delete(schedule_id)
            return {"success": True, "deleted_id": schedule_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # External Dynamic Lists
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_external_dynamic_lists(folder: str, tsg_id: str | None = None) -> list[dict] | dict:
        """List external dynamic lists (EDLs) in a folder.

        EDLs are feeds of IP addresses, URLs, or domains pulled from external
        sources (HTTP/HTTPS) and used in security policy.

        Args:
            folder: Folder name to scope the query.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).external_dynamic_list.list(folder=folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_external_dynamic_list(edl_id: str, tsg_id: str | None = None) -> dict:
        """Get a single external dynamic list by UUID.

        Args:
            edl_id: UUID of the external dynamic list.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).external_dynamic_list.get(edl_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_external_dynamic_list(
        name: str,
        folder: str,
        list_type: dict,
        tsg_id: str | None = None,
    ) -> dict:
        """Create an external dynamic list.

        Args:
            name: Unique name for the EDL.
            folder: Folder to create the EDL in.
            list_type: Type and source configuration dict. For an IP list:
                {'ip': {'url': 'https://feeds.example.com/blocklist.txt',
                        'recurring': {'daily': {'at': '01:00'}}}}.
                For a URL list: {'url': {'url': '...', 'recurring': {...}}}.
                For a domain list: {'domain': {'url': '...', 'recurring': {...}}}.
                The 'recurring' key controls fetch frequency:
                {'five_minute': {}}, {'hourly': {}}, {'daily': {'at': 'HH:MM'}},
                {'weekly': {'day_of_week': 'monday', 'at': 'HH:MM'}}.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "folder": folder, "type": list_type}
            return serialize(get_client(tsg_id).external_dynamic_list.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_external_dynamic_list(
        edl_id: str,
        name: str | None = None,
        list_type: dict | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing external dynamic list.

        Args:
            edl_id: UUID of the EDL to update.
            name: New name (optional).
            list_type: New type/source configuration dict (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            edl = client.external_dynamic_list.get(edl_id)
            if name is not None:
                edl.name = name
            if list_type is not None:
                edl.type = list_type
            return serialize(client.external_dynamic_list.update(edl))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_external_dynamic_list(edl_id: str, tsg_id: str | None = None) -> dict:
        """Delete an external dynamic list by UUID.

        Args:
            edl_id: UUID of the EDL to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).external_dynamic_list.delete(edl_id)
            return {"success": True, "deleted_id": edl_id}
        except Exception as exc:
            return handle_error(exc)
