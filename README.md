# StackRox MCP

Model Context Protocol (MCP) implementation for StackRox security platform. This enables Claude to interact directly with StackRox/RHACS APIs for security analysis, policy management, and vulnerability assessment.

**NOTES**

- Use of ADK has not been recently tested. There could be breaking changes.

## Prerequisites

- StackRox/RHACS cluster with Central deployed
- Kubernetes cluster access for Helm deployment

## Deployment

### OpenShift Deployment with Helm

```bash
export ROX_MCP_URL="https://your-stackrox-central-url"
```

**Default deployment** (uses built-in route configuration):

```bash
helm upgrade --install stackrox-mcp helm/stackrox-mcp \
  --namespace stackrox \
  --set image.repository="${DOCKER_REPO}" \
  --set image.tag="${IMAGE_TAG}" \
  --set env.roxUrl="${ROX_MCP_URL}"
```

**Custom routes deployment**:

```bash
helm upgrade --install stackrox-mcp helm/stackrox-mcp \
  --namespace stackrox \
  --set image.repository="${DOCKER_REPO}" \
  --set image.tag="${IMAGE_TAG}" \
  --set env.roxUrl="${ROX_MCP_URL}" \
  --values helm/stackrox-mcp/values-routes.yaml
```

## Claude Integration

### Adding StackRox MCP to Claude Desktop

1. **Get the MCP server URL**:
   ```bash
   export STACKROX_MCP_URL=$(kubectl get route -n stackrox stackrox-mcp -o jsonpath='{.spec.host}')
   ```

2. **Create and export a StackRox API Token**
   ```bash
   export STACKROX_API_TOKEN=<your-stackrox-api-token>
   ```

3. **Add MCP server to Claude Desktop configuration**:
    ```bash
    claude mcp add stackrox-mcp "http://${STACKROX_MCP_URL}/mcp" \
      --transport http \
      --header "Authorization: Bearer ${STACKROX_API_TOKEN}"
    ```

4. **Restart Claude Desktop** to load the new MCP server

5. **Test the integration**:
   - Open a new conversation in Claude
   - Use command: `/mcp` to check list of MCPs and their tools
   - Ask: "Can you list all clusters?" or "Show me the security policies"
   - Claude should now have access to StackRox APIs through the MCP server

### Available Commands

Once integrated, Claude can:
- List and analyze security alerts
- View and manage security policies
- Check deployment vulnerabilities
- Review CVE deferral requests
- Examine cluster and namespace information
- Provide security recommendations based on StackRox data

### Local Development

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Try it

### Local Development Setup

**1. Extract JWT private key from StackRox**:

```bash
kubectl get secret central-tls -n stackrox -o jsonpath='{.data.jwt-key\.pem}' | base64 -d > jwt-private-key.pem
```

**2. Generate JWKS file from private key**:

```bash
python scripts/generate_jwks.py --from-existing --private-key jwt-private-key.pem --output build/jwks.json
```

**3. Set environment variables**:

```bash
export FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER=true
export ROX_MCP_URL="https://your-stackrox-central-url"
export ROX_MCP_JWKS_FILE="build/jwks.json"
```

**4. Start the MCP server**:

```bash
python src/mcp/stackrox-mcp.py
```

The server will start on `http://localhost:8000` with the JWKS endpoint at `/jwks.json`.

### ADK Web Interface

**NOTE:** Outdated!

Run the ADK web interface:

```bash
cd tools/adk
adk web
```

Make sure to configure your `.env` file first (see `tools/adk/README.md` for setup instructions).

### Docker Container

**NOTE:** Outdated!

Build and run with Docker:

```bash
# Build the image
docker build -f Dockerfile-ADK -t stackrox-adk .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your-gcp-api-key \
  -e ROX_MCP_TOKEN=your-stackrox-token \
  -e ROX_MCP_URL=https://your-stackrox-instance.com \
  stackrox-adk
```

Access the web interface at `http://localhost:8000`
