"""SCM MCP Server — entry point.

Registers all tool modules and starts the server over stdio transport.
"""

from mcp.server.fastmcp import FastMCP

from src.tools import network, objects, operations, policy_objects, profiles, search, security, setup

mcp = FastMCP(
    name="scm",
    instructions=(
        "You are connected to Palo Alto Networks Strata Cloud Manager (SCM). "
        "Use these tools to manage firewall configuration including folders, snippets, "
        "security policies, address objects, service objects, NAT rules, security zones, "
        "and security profiles. "
        "Always confirm destructive operations (delete, commit) with the user before proceeding. "
        "When creating objects, specify the folder scope. "
        "After making configuration changes, use scm_commit to push changes to devices. "
        "Use scm_list_tsg_profiles to see available TSG tenants. Pass tsg_id to any tool "
        "to target a specific tenant (use named alias like 'PROD' or a raw TSG ID)."
    ),
)

# Register all tool modules
setup.register(mcp)
objects.register(mcp)
policy_objects.register(mcp)
security.register(mcp)
network.register(mcp)
profiles.register(mcp)
operations.register(mcp)
search.register(mcp)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
