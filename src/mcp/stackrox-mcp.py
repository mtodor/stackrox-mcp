import json
import os
from pathlib import Path

import httpx
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, MCPType
from httpx import BasicAuth

# Create an HTTP client for your API with basic auth
url = os.getenv("ROX_MCP_URL", "https://localhost:8443")

token = os.getenv("ROX_MCP_TOKEN", "")
if token:
    client = httpx.AsyncClient(base_url=url, headers={"Authorization": f"Bearer {token}"}, verify=False)
else:
    username = os.getenv("ROX_MCP_USERNAME", "admin")
    password = os.getenv("ROX_MCP_PASSWORD", "")
    client = httpx.AsyncClient(base_url=url, auth=BasicAuth(username=username, password=password), verify=False)

# Load your OpenAPI spec from local file
openapi_file = Path(__file__).parent / "../../specs/stackrox-api-no-refs.json"
openapi_spec = json.loads(openapi_file.read_text())

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="StackRox MCP Server",
    route_maps=[
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/alerts$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/alerts/{id}$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/cve/requests.*",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["POST"],
            pattern=r"^/v1/cve/requests.*",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/clusters$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/namespaces$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/deployments$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/deploymentswithrisk/{id}$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/policies$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/policies/{id}$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["POST", "PUT"],
            pattern=r"^/v1/policies$|^/v1/policies/{id}$",
            mcp_type=MCPType.TOOL,
        ),

        # Exclude all remaining routes
        RouteMap(mcp_type=MCPType.EXCLUDE),
    ],

)

if __name__ == "__main__":
    mcp.run()
