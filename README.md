# scm-mcp

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for [Palo Alto Networks Strata Cloud Manager (SCM)](https://www.paloaltonetworks.com/sase/strata-cloud-manager). Exposes 149 tools covering the full SCM configuration lifecycle — policy objects, security rules, NAT, profiles, decryption, QoS, and more — so you can manage firewall configuration through natural language in Claude Code or Claude Desktop.

## Features

- **149 tools** across 9 functional areas
- **Multi-tenant (multi-TSG) support** — target different tenants per tool call with named aliases
- **Full CRUD** for all supported resource types
- **Zero infrastructure** — runs as a local stdio process, no server to maintain
- Built on the [pan-scm-sdk](https://github.com/cdot65/pan-scm-sdk) which handles OAuth2 token lifecycle, pagination, and Pydantic validation automatically

## Tool Coverage

| Area | Tools | Resources |
|------|------:|-----------|
| Setup | 12 | Folders, Snippets |
| Objects | 45 | Addresses, Address Groups, Services, Service Groups, Tags, Log Forwarding Profiles, HTTP Server Profiles, Syslog Server Profiles |
| Policy Objects | 24 | Applications, Application Groups, Application Filters, Schedules, External Dynamic Lists |
| Security | 26 | Security Rules, Security Zones, Decryption Rules, Authentication Rules |
| Network | 17 | NAT Rules, PBF Rules, QoS Rules |
| Profiles | 24 | Anti-Spyware, WildFire, Vulnerability, URL Access, URL Categories, DNS Security, Decryption, File Blocking, Zone Protection |
| Operations | 4 | Commit, Job Status, List Jobs, List TSG Profiles |
| **Total** | **149** | |

## Requirements

- Python 3.12+
- A Palo Alto Networks SCM tenant with a service account
- [Claude Code](https://claude.ai/code) or [Claude Desktop](https://claude.ai/download)

## Installation

### 1. Clone and install

```bash
git clone https://github.com/your-username/scm-mcp.git
cd scm-mcp
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your SCM service account credentials:

```env
SCM_CLIENT_ID=your_client_id_here
SCM_CLIENT_SECRET=your_client_secret_here
SCM_TSG_ID=your_default_tsg_id_here

# Optional: named aliases for multi-tenant use
# SCM_TSG_PROD=prod_tsg_id_here
# SCM_TSG_LAB=lab_tsg_id_here
```

> **Where to find credentials:** SCM portal → Settings → Service Accounts → Create. The TSG ID appears in the tenant URL: `https://stratacloudmanager.paloaltonetworks.com/tenants/<TSG_ID>/`.

### 3. Register with Claude Code

```bash
claude mcp add scm -- /path/to/scm-mcp/.venv/bin/python -m src.server
```

Or add to `.claude/settings.json` manually:

```json
{
  "mcpServers": {
    "scm": {
      "command": "/path/to/scm-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/scm-mcp"
    }
  }
}
```

### 4. Register with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "scm": {
      "command": "/path/to/scm-mcp/.venv/bin/python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/scm-mcp",
      "env": {
        "SCM_CLIENT_ID": "your_client_id",
        "SCM_CLIENT_SECRET": "your_client_secret",
        "SCM_TSG_ID": "your_tsg_id"
      }
    }
  }
}
```

## Multi-Tenant Usage

Every tool accepts an optional `tsg_id` parameter. When omitted, the default `SCM_TSG_ID` is used.

**Named aliases** — define them in `.env`:
```env
SCM_TSG_PROD=1234567890
SCM_TSG_LAB=9876543210
```

Then pass the alias name to any tool:
```
# List which TSGs are configured
scm_list_tsg_profiles()

# Query the PROD tenant
scm_list_addresses(folder="All", tsg_id="PROD")

# Copy an object between tenants
scm_get_address(address_id="<uuid>", tsg_id="PROD")
scm_create_address(name="web-servers", folder="Texas", ip_netmask="10.0.1.0/24", tsg_id="LAB")
```

You can also pass a raw TSG ID string directly if no alias is configured.

## Project Structure

```
scm-mcp/
├── src/
│   ├── server.py            # MCP server entry point and tool registration
│   ├── client.py            # Per-TSG Scm client factory with alias resolution
│   ├── utils.py             # Serialization (Pydantic → dict) and error handling
│   └── tools/
│       ├── setup.py         # Folders, Snippets
│       ├── objects.py       # Addresses, Address Groups, Services, Service Groups,
│       │                    #   Tags, Log/HTTP/Syslog Server Profiles
│       ├── policy_objects.py# Applications, App Groups, App Filters,
│       │                    #   Schedules, External Dynamic Lists
│       ├── security.py      # Security Rules, Security Zones,
│       │                    #   Decryption Rules, Authentication Rules
│       ├── network.py       # NAT Rules, PBF Rules, QoS Rules
│       ├── profiles.py      # Anti-Spyware, WildFire, Vulnerability, URL Access,
│       │                    #   URL Categories, DNS Security, Decryption,
│       │                    #   File Blocking, Zone Protection Profiles
│       └── operations.py    # Commit, Job Status, List Jobs, List TSG Profiles
├── .env.example             # Credential template (commit this)
├── .env                     # Real credentials (gitignored)
├── pyproject.toml           # Project metadata and dependencies
└── README.md
```

## Example Prompts

Once the MCP server is connected, you can use natural language in Claude Code:

```
Show me all security rules in the Texas folder.

Create an address object for our web server farm: 10.10.1.0/24 in the Texas folder, tagged "web-tier".

Copy all address objects from the PROD tenant into the LAB tenant under the same folder.

Create a security rule allowing HTTPS from the trust zone to the DMZ zone for the web-servers address group. Use the best-practice security profile group.

What external dynamic lists are configured and when do they refresh?

Commit the changes in the Texas and California folders with description "Q2 policy update".
```

## Tool Reference

### Operations

| Tool | Description |
|------|-------------|
| `scm_list_tsg_profiles` | List configured TSG profiles and their aliases |
| `scm_commit` | Commit staged changes and push to devices |
| `scm_get_job_status` | Poll an async commit job for completion |
| `scm_list_jobs` | List recent SCM jobs |

### Setup

| Tool | Description |
|------|-------------|
| `scm_list_folders` | List all folders |
| `scm_get_folder` | Get folder by UUID |
| `scm_create_folder` | Create a folder |
| `scm_update_folder` | Rename or redescribe a folder |
| `scm_delete_folder` | Delete a folder |
| `scm_list_snippets` | List all snippets |
| `scm_get_snippet` | Get snippet by UUID |
| `scm_create_snippet` | Create a snippet |
| `scm_update_snippet` | Update a snippet |
| `scm_delete_snippet` | Delete a snippet |
| `scm_associate_snippet_to_folder` | Associate a snippet with a folder |
| `scm_disassociate_snippet_from_folder` | Remove snippet-folder association |

### Objects

| Tool | Description |
|------|-------------|
| `scm_list_addresses` | List address objects |
| `scm_get_address` | Get address by UUID |
| `scm_create_address` | Create an address (IP/CIDR, range, wildcard, or FQDN) |
| `scm_update_address` | Update an address |
| `scm_delete_address` | Delete an address |
| `scm_list_address_groups` | List address groups |
| `scm_get_address_group` | Get address group by UUID |
| `scm_create_address_group` | Create a static or dynamic address group |
| `scm_update_address_group` | Update an address group |
| `scm_delete_address_group` | Delete an address group |
| `scm_list_services` | List service objects |
| `scm_get_service` | Get service by UUID |
| `scm_create_service` | Create a TCP/UDP service |
| `scm_update_service` | Update a service |
| `scm_delete_service` | Delete a service |
| `scm_list_service_groups` | List service groups |
| `scm_get_service_group` | Get service group by UUID |
| `scm_create_service_group` | Create a service group |
| `scm_update_service_group` | Update a service group |
| `scm_delete_service_group` | Delete a service group |
| `scm_list_tags` | List tags |
| `scm_get_tag` | Get tag by UUID |
| `scm_create_tag` | Create a tag |
| `scm_update_tag` | Update a tag |
| `scm_delete_tag` | Delete a tag |
| `scm_list_log_forwarding_profiles` | List log forwarding profiles |
| `scm_get_log_forwarding_profile` | Get log forwarding profile by UUID |
| `scm_create_log_forwarding_profile` | Create a log forwarding profile |
| `scm_delete_log_forwarding_profile` | Delete a log forwarding profile |
| `scm_list_http_server_profiles` | List HTTP server profiles |
| `scm_get_http_server_profile` | Get HTTP server profile by UUID |
| `scm_create_http_server_profile` | Create an HTTP server profile |
| `scm_delete_http_server_profile` | Delete an HTTP server profile |
| `scm_list_syslog_server_profiles` | List syslog server profiles |
| `scm_get_syslog_server_profile` | Get syslog server profile by UUID |
| `scm_create_syslog_server_profile` | Create a syslog server profile |
| `scm_delete_syslog_server_profile` | Delete a syslog server profile |

### Policy Objects

| Tool | Description |
|------|-------------|
| `scm_list_applications` | List application objects |
| `scm_get_application` | Get application by UUID |
| `scm_create_application` | Create a custom application |
| `scm_update_application` | Update a custom application |
| `scm_delete_application` | Delete a custom application |
| `scm_list_application_groups` | List application groups |
| `scm_get_application_group` | Get application group by UUID |
| `scm_create_application_group` | Create an application group |
| `scm_update_application_group` | Update an application group |
| `scm_delete_application_group` | Delete an application group |
| `scm_list_application_filters` | List application filters |
| `scm_get_application_filter` | Get application filter by UUID |
| `scm_create_application_filter` | Create a dynamic application filter |
| `scm_delete_application_filter` | Delete an application filter |
| `scm_list_schedules` | List schedule objects |
| `scm_get_schedule` | Get schedule by UUID |
| `scm_create_schedule` | Create a recurring or one-time schedule |
| `scm_update_schedule` | Update a schedule |
| `scm_delete_schedule` | Delete a schedule |
| `scm_list_external_dynamic_lists` | List external dynamic lists (EDLs) |
| `scm_get_external_dynamic_list` | Get EDL by UUID |
| `scm_create_external_dynamic_list` | Create an IP/URL/domain EDL |
| `scm_update_external_dynamic_list` | Update an EDL |
| `scm_delete_external_dynamic_list` | Delete an EDL |

### Security

| Tool | Description |
|------|-------------|
| `scm_list_security_rules` | List security policy rules |
| `scm_get_security_rule` | Get security rule by UUID |
| `scm_create_security_rule` | Create a security rule |
| `scm_update_security_rule` | Update a security rule |
| `scm_delete_security_rule` | Delete a security rule |
| `scm_move_security_rule` | Reorder a rule (top/bottom/before/after) |
| `scm_list_security_zones` | List security zones |
| `scm_get_security_zone` | Get security zone by UUID |
| `scm_create_security_zone` | Create a security zone |
| `scm_update_security_zone` | Update a security zone |
| `scm_delete_security_zone` | Delete a security zone |
| `scm_list_decryption_rules` | List decryption policy rules |
| `scm_get_decryption_rule` | Get decryption rule by UUID |
| `scm_create_decryption_rule` | Create a decrypt/no-decrypt rule |
| `scm_update_decryption_rule` | Update a decryption rule |
| `scm_delete_decryption_rule` | Delete a decryption rule |
| `scm_list_authentication_rules` | List authentication policy rules |
| `scm_get_authentication_rule` | Get authentication rule by UUID |
| `scm_create_authentication_rule` | Create an authentication rule |
| `scm_update_authentication_rule` | Update an authentication rule |
| `scm_delete_authentication_rule` | Delete an authentication rule |

### Network

| Tool | Description |
|------|-------------|
| `scm_list_nat_rules` | List NAT rules |
| `scm_get_nat_rule` | Get NAT rule by UUID |
| `scm_create_nat_rule` | Create a NAT rule (IPv4, NAT64, NPTv6) |
| `scm_update_nat_rule` | Update a NAT rule |
| `scm_delete_nat_rule` | Delete a NAT rule |
| `scm_list_pbf_rules` | List policy-based forwarding rules |
| `scm_get_pbf_rule` | Get PBF rule by UUID |
| `scm_create_pbf_rule` | Create a PBF rule |
| `scm_update_pbf_rule` | Update a PBF rule |
| `scm_delete_pbf_rule` | Delete a PBF rule |
| `scm_list_qos_rules` | List QoS policy rules |
| `scm_get_qos_rule` | Get QoS rule by UUID |
| `scm_create_qos_rule` | Create a QoS rule |
| `scm_update_qos_rule` | Update a QoS rule |
| `scm_delete_qos_rule` | Delete a QoS rule |

### Security Profiles

| Tool | Description |
|------|-------------|
| `scm_list_anti_spyware_profiles` | List anti-spyware profiles |
| `scm_get_anti_spyware_profile` | Get anti-spyware profile by UUID |
| `scm_create_anti_spyware_profile` | Create an anti-spyware profile |
| `scm_delete_anti_spyware_profile` | Delete an anti-spyware profile |
| `scm_list_wildfire_profiles` | List WildFire antivirus profiles |
| `scm_get_wildfire_profile` | Get WildFire profile by UUID |
| `scm_create_wildfire_profile` | Create a WildFire profile |
| `scm_delete_wildfire_profile` | Delete a WildFire profile |
| `scm_list_vulnerability_profiles` | List vulnerability protection profiles |
| `scm_get_vulnerability_profile` | Get vulnerability profile by UUID |
| `scm_create_vulnerability_profile` | Create a vulnerability protection profile |
| `scm_delete_vulnerability_profile` | Delete a vulnerability protection profile |
| `scm_list_url_access_profiles` | List URL access (filtering) profiles |
| `scm_get_url_access_profile` | Get URL access profile by UUID |
| `scm_create_url_access_profile` | Create a URL access profile |
| `scm_delete_url_access_profile` | Delete a URL access profile |
| `scm_list_url_categories` | List custom URL categories |
| `scm_get_url_category` | Get URL category by UUID |
| `scm_create_url_category` | Create a custom URL category |
| `scm_delete_url_category` | Delete a custom URL category |
| `scm_list_dns_security_profiles` | List DNS security profiles |
| `scm_get_dns_security_profile` | Get DNS security profile by UUID |
| `scm_create_dns_security_profile` | Create a DNS security profile |
| `scm_delete_dns_security_profile` | Delete a DNS security profile |
| `scm_list_decryption_profiles` | List SSL/TLS decryption profiles |
| `scm_get_decryption_profile` | Get decryption profile by UUID |
| `scm_create_decryption_profile` | Create a decryption profile |
| `scm_delete_decryption_profile` | Delete a decryption profile |
| `scm_list_file_blocking_profiles` | List file blocking profiles |
| `scm_get_file_blocking_profile` | Get file blocking profile by UUID |
| `scm_create_file_blocking_profile` | Create a file blocking profile |
| `scm_delete_file_blocking_profile` | Delete a file blocking profile |
| `scm_list_zone_protection_profiles` | List zone protection profiles |
| `scm_get_zone_protection_profile` | Get zone protection profile by UUID |
| `scm_create_zone_protection_profile` | Create a zone protection profile |
| `scm_delete_zone_protection_profile` | Delete a zone protection profile |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SCM_CLIENT_ID` | Yes | OAuth2 client ID from the SCM service account |
| `SCM_CLIENT_SECRET` | Yes | OAuth2 client secret from the SCM service account |
| `SCM_TSG_ID` | Yes | Default Tenant Service Group ID |
| `SCM_TSG_<NAME>` | No | Named TSG alias — pass `<NAME>` as `tsg_id` to any tool |

## Authentication

SCM uses OAuth2 client credentials flow. Tokens have a 15-minute TTL and are automatically refreshed by the underlying `pan-scm-sdk`. No token management is required.

Service accounts are created in the SCM portal under **Settings > Identity & Access > Service Accounts**. The account needs appropriate role permissions for the resources you intend to manage.

## Contributing

Issues and pull requests welcome. This project is built on [pan-scm-sdk](https://github.com/cdot65/pan-scm-sdk) — if you need a resource type that isn't covered here, check whether the SDK supports it first.

## License

MIT
