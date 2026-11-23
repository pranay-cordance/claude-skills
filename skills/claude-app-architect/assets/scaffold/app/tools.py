"""Custom tools, exposed in-process as an SDK MCP server.

Write tools should return a draft and leave the real side effect to an
approved step. The approval itself is enforced in agent.py (can_use_tool),
not in the prompt.
"""
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool(
    "create_story_draft",
    "Create a DRAFT user story in Jira for human review. Does not publish.",
    {"title": str, "description": str, "acceptance_criteria": list},
)
async def create_story_draft(args):
    # TODO: call the Jira API as the end user (OAuth), in draft state.
    draft_id = "DRAFT-001"
    return {"content": [{"type": "text", "text": f"Draft created: {draft_id}"}]}


kairo_tools = create_sdk_mcp_server(
    name="kairo", version="0.1.0", tools=[create_story_draft]
)

WRITE_TOOLS = {"mcp__kairo__create_story_draft"}
