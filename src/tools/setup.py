"""Tools for SCM setup resources: Folders and Snippets."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all setup tools on the given FastMCP instance."""

    # -------------------------------------------------------------------------
    # Folders
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_folders(tsg_id: str | None = None) -> list[dict] | dict:
        """List all folders in Strata Cloud Manager.

        Returns a list of folder objects. Folders form the container hierarchy
        used to scope firewall configuration (policies, objects, etc.).

        Args:
            tsg_id: Optional TSG ID or named alias (e.g. 'PROD'). Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).folder.list())
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_folder(folder_id: str, tsg_id: str | None = None) -> dict:
        """Get a single folder by its UUID.

        Args:
            folder_id: The UUID of the folder to retrieve.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).folder.get(folder_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_folder(
        name: str,
        parent: str,
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a new folder in Strata Cloud Manager.

        Args:
            name: Unique name for the folder.
            parent: Name of the parent folder (e.g. 'All', 'Texas').
            description: Optional human-readable description.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name, "parent": parent}
            if description:
                data["description"] = description
            return serialize(get_client(tsg_id).folder.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_folder(
        folder_id: str,
        name: str | None = None,
        description: str | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing folder.

        Fetch the folder first, modify the returned object, then pass it to
        this tool. At least one of name or description must be provided.

        Args:
            folder_id: UUID of the folder to update.
            name: New name for the folder (optional).
            description: New description (optional).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            folder = client.folder.get(folder_id)
            if name is not None:
                folder.name = name
            if description is not None:
                folder.description = description
            return serialize(client.folder.update(folder))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_folder(folder_id: str, tsg_id: str | None = None) -> dict:
        """Delete a folder by its UUID.

        WARNING: This is irreversible. Ensure the folder has no dependent
        configuration objects before deleting.

        Args:
            folder_id: UUID of the folder to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).folder.delete(folder_id)
            return {"success": True, "deleted_id": folder_id}
        except Exception as exc:
            return handle_error(exc)

    # -------------------------------------------------------------------------
    # Snippets
    # -------------------------------------------------------------------------

    @mcp.tool()
    def scm_list_snippets(tsg_id: str | None = None) -> list[dict] | dict:
        """List all configuration snippets in Strata Cloud Manager.

        Snippets are reusable configuration elements that can be associated
        with folders or devices. They allow shared config to be applied to
        a subset of firewalls without full folder inheritance.

        Args:
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).snippet.list())
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_snippet(snippet_id: str, tsg_id: str | None = None) -> dict:
        """Get a single snippet by its UUID.

        Args:
            snippet_id: The UUID of the snippet to retrieve.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).snippet.get(snippet_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_create_snippet(
        name: str,
        description: str | None = None,
        labels: list[str] | None = None,
        enable_prefix: bool = False,
        tsg_id: str | None = None,
    ) -> dict:
        """Create a new configuration snippet.

        Args:
            name: Unique name for the snippet.
            description: Optional human-readable description.
            labels: Optional list of label strings for categorization.
            enable_prefix: Whether to enable name prefixing (default False).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            data: dict = {"name": name}
            if description:
                data["description"] = description
            if labels:
                data["labels"] = labels
            if enable_prefix:
                data["enable_prefix"] = enable_prefix
            return serialize(get_client(tsg_id).snippet.create(data))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_update_snippet(
        snippet_id: str,
        name: str | None = None,
        description: str | None = None,
        labels: list[str] | None = None,
        tsg_id: str | None = None,
    ) -> dict:
        """Update an existing snippet's metadata.

        Args:
            snippet_id: UUID of the snippet to update.
            name: New name (optional).
            description: New description (optional).
            labels: New label list (optional — replaces existing labels).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            snippet = client.snippet.get(snippet_id)
            if name is not None:
                snippet.name = name
            if description is not None:
                snippet.description = description
            if labels is not None:
                snippet.labels = labels
            return serialize(client.snippet.update(snippet))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_delete_snippet(snippet_id: str, tsg_id: str | None = None) -> dict:
        """Delete a snippet by its UUID.

        WARNING: This is irreversible. Disassociate the snippet from all
        folders and devices before deleting.

        Args:
            snippet_id: UUID of the snippet to delete.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            get_client(tsg_id).snippet.delete(snippet_id)
            return {"success": True, "deleted_id": snippet_id}
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_associate_snippet_to_folder(
        snippet_id: str,
        folder_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Associate a snippet with a folder.

        Once associated, the snippet's configuration is applied to firewalls
        in that folder.

        Args:
            snippet_id: UUID of the snippet.
            folder_id: UUID of the folder to associate with.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).snippet.associate_folder(snippet_id, folder_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_disassociate_snippet_from_folder(
        snippet_id: str,
        folder_id: str,
        tsg_id: str | None = None,
    ) -> dict:
        """Remove the association between a snippet and a folder.

        Args:
            snippet_id: UUID of the snippet.
            folder_id: UUID of the folder to disassociate from.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).snippet.disassociate_folder(snippet_id, folder_id))
        except Exception as exc:
            return handle_error(exc)
