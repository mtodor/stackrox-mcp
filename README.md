# StackRox MCP

Model Context Protocol (MCP) implementation for StackRox security platform.

## Install

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Try it

### Local Development

Run the ADK web interface:

```bash
cd tools/adk
adk web
```

Make sure to configure your `.env` file first (see `tools/adk/README.md` for setup instructions).

### Docker Container

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
