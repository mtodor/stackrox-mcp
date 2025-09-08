import json
import logging
import os
from pathlib import Path

import httpx
from fastapi.responses import JSONResponse
from fastmcp import FastMCP

### FastMCP
# FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER=true
from fastmcp.experimental.server.openapi import RouteMap, MCPType
from fastmcp.server.auth.providers.jwt import JWTVerifier
from httpx import BasicAuth

# Create an HTTP client for your API with basic auth
url = os.getenv("ROX_MCP_URL", "https://localhost:8443")
logging.warning(f"Using url: {url}")

token = os.getenv("ROX_MCP_TOKEN", "")
username = os.getenv("ROX_MCP_USERNAME", "")
password = os.getenv("ROX_MCP_PASSWORD", "")

if token:
    logging.warning(f"🔑 Using ACS token: {token[:10]}...")
    client = httpx.AsyncClient(base_url=url, headers={"Authorization": f"Bearer {token}"}, verify=False)
elif username and password:
    logging.warning("Using basic authentication")
    client = httpx.AsyncClient(base_url=url, auth=BasicAuth(username=username, password=password), verify=False)
else:
    logging.warning("No authentication provided - creating client without auth")
    client = httpx.AsyncClient(base_url=url, verify=False)

# Load your OpenAPI spec from local file
openapi_spec_path = os.getenv("ROX_MCP_OPENAPI_SPEC", "stackrox-mcp-api-no-refs.json")
openapi_file = Path(__file__).parent / f"../../specs/{openapi_spec_path}"
openapi_spec = json.loads(openapi_file.read_text())

# Configure JWT authentication
jwks_uri = os.getenv("ROX_MCP_JWT_JWKS_URI", "http://localhost:8000/jwks.json")
issuer = os.getenv("ROX_MCP_JWT_ISSUER", "https://stackrox.io/jwt")
audience = os.getenv("ROX_MCP_JWT_AUDIENCE", "https://stackrox.io/jwt-sources#api-tokens")

auth = JWTVerifier(jwks_uri=jwks_uri, issuer=issuer, audience=audience)

# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="StackRox MCP Server",
    auth=auth,
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
            pattern=r"^/v1/clusters$",
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
            pattern=r"^/v1/deployments$",
            mcp_type=MCPType.TOOL,
        ),
        RouteMap(
            methods=["GET"],
            pattern=r"^/v1/namespaces$",
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


# Add JWKS endpoint using the underlying FastAPI app
@mcp.custom_route("/jwks.json", methods=["GET"])
async def get_jwks(request):
    """Serve JWKS file for JWT verification."""
    jwks_file = Path(__file__).parent / "../../jwks.json"
    if jwks_file.exists():
        return JSONResponse(content=json.loads(jwks_file.read_text()))
    return JSONResponse(content={"keys": []})


if __name__ == "__main__":
    # Run as HTTP server instead of stdio
    port = int(os.getenv("ROX_MCP_PORT", "8000"))
    host = os.getenv("ROX_MCP_HOST", "0.0.0.0")

    mcp.run(transport="http", host=host, port=port)
