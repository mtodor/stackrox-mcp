import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
from google.genai.types import GenerateContentConfig
from phoenix.otel import register

STACKROX_MCP_PATH = Path(__file__).parent / "../../../src/mcp/stackrox-mcp.py"

def is_enabled(env_var: str) -> bool:
    return os.environ.get(env_var, "").lower() in ("true", "1", "yes", "on")

if is_enabled("PHOENIX_ENABLED"):
    tracer_provider = register(
        project_name="stackrox-agent",
        auto_instrument=True,
    )

root_agent = LlmAgent(
    model=os.environ.get("AI_MODEL_NAME", "gemini-2.5-pro"),
    name='stackrox_ai_agent',
    instruction='You are an advanced cluster security agent specialized in using Red Hat Advanced Cluster Security for Kubernetes. Your goal is to help the user with their security needs.',
    generate_content_config=GenerateContentConfig(
        temperature=0.8
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='fastmcp',
                    args=[
                        "run",
                        f"{STACKROX_MCP_PATH}:mcp",
                    ],
                    env={
                        "ROX_MCP_TOKEN": os.environ.get("ROX_MCP_TOKEN", ""),
                        "ROX_MCP_PASSWORD": os.environ.get("ROX_MCP_PASSWORD", ""),
                        "ROX_MCP_URL": os.environ.get("ROX_MCP_URL", ""),
                    },
                ),
                timeout=120,
            ),
        ),
    ],
)
