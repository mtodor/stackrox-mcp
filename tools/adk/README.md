# StackRox ADK

Agent Development Kit for StackRox security platform.

## Setup

1. Copy the environment template:
   ```bash
   cp .env-example .env
   ```

2. Set your values in the `.env` file:
   ```bash
   # Google Modle Configuration
   GOOGLE_API_KEY=your-gcp-api-key
   # StackRox Configuration
   ROX_MCP_TOKEN=your-stackrox-token
   ROX_MCP_URL=https://your-stackrox-instance.com
   ```

## Run

Navigate to the `tools/adk` folder and run:

```bash
cd tools/adk
adk web
```
