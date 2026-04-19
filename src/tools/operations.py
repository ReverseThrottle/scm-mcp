"""Tools for SCM operations: Commit, job status, and TSG profile listing."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from src.client import get_client, list_tsg_profiles
from src.utils import handle_error, serialize


def register(mcp: FastMCP) -> None:
    """Register all operations tools on the given FastMCP instance."""

    @mcp.tool()
    def scm_list_tsg_profiles() -> list[dict]:
        """List configured TSG profiles available to the server.

        Returns names and env var aliases for all configured TSGs. Use the
        'name' value as the tsg_id argument in any other SCM tool.

        The 'default' profile is used when tsg_id is omitted or null.
        """
        return list_tsg_profiles()

    @mcp.tool()
    def scm_commit(
        folders: list[str],
        description: str | None = None,
        sync: bool = True,
        timeout: int = 300,
        tsg_id: str | None = None,
    ) -> dict:
        """Commit pending configuration changes and push to devices.

        This pushes staged changes in the specified folders to the managed
        firewalls. The operation is asynchronous — use sync=True to wait for
        completion (up to timeout seconds) or sync=False to get a job ID
        immediately.

        Args:
            folders: List of folder names whose changes should be committed
                (e.g. ['Texas', 'California']).
            description: Optional commit description shown in the audit log.
            sync: Wait for the commit job to complete before returning (default True).
            timeout: Seconds to wait when sync=True (default 300).
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            result = get_client(tsg_id).commit(
                folders=folders,
                description=description or "Committed via SCM MCP",
                sync=sync,
                timeout=timeout,
            )
            return serialize(result)
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_get_job_status(job_id: str, tsg_id: str | None = None) -> dict:
        """Get the status of an SCM job (e.g. a commit job).

        Args:
            job_id: The job UUID returned by scm_commit or another async operation.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            return serialize(get_client(tsg_id).get_job_status(job_id))
        except Exception as exc:
            return handle_error(exc)

    @mcp.tool()
    def scm_list_jobs(
        parent_id: str | None = None,
        tsg_id: str | None = None,
    ) -> list[dict] | dict:
        """List recent SCM jobs.

        Args:
            parent_id: Optional parent job UUID to filter child jobs.
            tsg_id: Optional TSG ID or named alias. Defaults to SCM_TSG_ID.
        """
        try:
            client = get_client(tsg_id)
            kwargs: dict = {}
            if parent_id:
                kwargs["parent_id"] = parent_id
            return serialize(client.list_jobs(**kwargs))
        except Exception as exc:
            return handle_error(exc)
