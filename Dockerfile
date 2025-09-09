FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the MCP server code and specs
COPY src/mcp/ ./src/mcp/
COPY specs/stackrox-api-no-refs-nullable.json ./specs/
COPY scripts/entrypoint.sh ./scripts/
COPY scripts/generate_jwks.py ./scripts/
COPY config/ ./config/

# Set environment variables with defaults
ENV ROX_MCP_PORT=8000
ENV ROX_MCP_HOST=0.0.0.0
ENV ROX_MCP_URL=https://localhost:8443
ENV ROX_MCP_TOKEN=test

# Set FastMCP experimentation flag
ENV FASTMCP_EXPERIMENTAL_ENABLE_NEW_OPENAPI_PARSER=true

# Expose the port
EXPOSE 8000

# Make entrypoint script executable
RUN chmod +x scripts/entrypoint.sh

# Run the entrypoint script
CMD ["scripts/entrypoint.sh"]
