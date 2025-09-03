#!/bin/bash
set -e

echo "🔑 Generating JWKS from mounted private key..."

# Generate JWKS from mounted private key
python scripts/generate_jwks.py --from-existing --private-key /tmp/jwt-key.pem
mv build/jwks.json ./jwks.json

echo "🚀 Starting StackRox MCP Server..."

# Start the MCP server
python src/mcp/stackrox-mcp.py
