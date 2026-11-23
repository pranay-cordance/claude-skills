# Claude building blocks

Check current details before writing code:
- Claude API docs map: https://docs.claude.com/en/docs_site_map.md
- Agent SDK overview: https://docs.claude.com/en/api/agent-sdk/overview (also mirrored at code.claude.com/docs)
- Agent Skills: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
- Claude on Bedrock: https://docs.claude.com/en/api/claude-on-amazon-bedrock

## Contents
1. Model tiers
2. Messages API features
3. Agent SDK
4. MCP
5. Agent Skills
6. Retrieval (RAG)
7. Feature availability by provider

## 1. Model tiers

Claude comes in three tiers: Haiku (fastest and cheapest; good for classification, extraction and routing), Sonnet (the default for agents and coding), and Opus (the hardest reasoning and long multi-step work). Read the current model IDs from the models page or the Bedrock console, and put them in config. Never hardcode them.

## 2. Messages API features

| Feature | Use it for |
|---|---|
| Tool use (client tools) | Your code runs the tool; Claude decides when to call it |
| Server tools (web search, web fetch, code execution) | Anthropic runs the tool |
| Structured outputs | Responses guaranteed to match a JSON schema, for rung-1 and rung-2 steps |
| Prompt caching | Cheaper and faster repeated prefixes: system prompt, tools, large documents |
| Extended thinking | Hard reasoning steps; budget it |
| Citations | Grounded answers over supplied documents |
| Message Batches | Bulk offline jobs at lower cost, such as nightly feedback analysis |
| Files API | Upload once, reference many times |

## 3. Agent SDK (Python and TypeScript)

The SDK runs the same agent engine as Claude Code as a library. You get the loop, built-in tools (Read, Write, Edit, Bash, Glob, Grep, WebFetch and others), MCP clients, Skills, subagents, hooks, permission modes and sessions.

Typical shape (Python; verify names against current docs):

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition

options = ClaudeAgentOptions(
    system_prompt="You are KAIRO's product & engineering assistant...",
    model=settings.default_model,                 # from config, not hardcoded
    cwd="/workspace/session-123",                 # per-session working dir
    setting_sources=["project"],                  # loads .claude/skills from cwd
    allowed_tools=["Skill", "Read", "mcp__jira__search_issues"],
    mcp_servers={"jira": jira_server_config},
    agents={
        "spec-writer": AgentDefinition(
            description="Turns requirements into structured specs and user stories",
            prompt="...", tools=["Skill", "Read", "mcp__jira__search_issues"],
        ),
    },
    permission_mode="default",
)
async for msg in query(prompt=user_request, options=options):
    ...
```

Controls that matter in the enterprise:
- **`allowed_tools` / `disallowed_tools`** set a per-role tool allowlist. This is how RBAC is enforced.
- **The `can_use_tool` callback and `PreToolUse` hooks** implement human-in-the-loop approval, policy checks and audit logging before any side effect.
- **`PostToolUse` hooks** handle redaction and logging of tool results.
- **Subagents** give each capability an isolated context and its own tools, and return summaries to the orchestrator.
- **Custom tools** can run in-process as SDK MCP servers (the `@tool` decorator plus `create_sdk_mcp_server`), with no separate service to deploy.

Provider switch: setting `CLAUDE_CODE_USE_BEDROCK=1` plus AWS credentials and region moves the SDK onto Bedrock, with no code change.

## 4. MCP (Model Context Protocol)

Wrap each system of record (Jira/Coda, Git, CRM, Zendesk, Snowflake, SharePoint) as an MCP server. One server can then serve the web app agent, the IDE (Claude Code) and claude.ai.
- Prefer existing official servers. Build your own only for internal systems.
- Expose small, task-shaped tools (`search_issues`, `get_issue`, `create_issue`) rather than raw query endpoints.
- Authenticate as the end user where possible (OAuth), so the agent can never see more than that user can.
- Transport: stdio for in-container servers; Streamable HTTP for shared remote servers.

## 5. Agent Skills

A Skill is a folder containing a `SKILL.md` (YAML `name` and `description`, then instructions) plus optional `scripts/`, `references/` and `assets/`. Only the name and description sit in context until the Skill is triggered, so many Skills cost little.
- Use Skills for procedures, templates, house style and domain knowledge: "how we write user stories", "our pricing rules".
- In the Agent SDK, place Skills in `.claude/skills/` and enable them with `setting_sources` plus the `Skill` tool.
- On the Claude API, Skills are uploaded through the Skills API (`/v1/skills`) and used with the code-execution tool.
- Deployment channels are covered by the `claude-aws-deploy` skill.

## 6. Retrieval (RAG)

- Use hybrid retrieval (BM25 plus embeddings, e.g. bge-m3) with a reranker, chunking along document structure, and attach source metadata for citations.
- Expose it to agents as one MCP tool, `search_knowledge(query, filters)`, that returns chunks with source, URL and permissions.
- Enforce document ACLs inside the retrieval service, not in the prompt.
- Consider contextual retrieval, which prepends a short chunk-specific summary before embedding, for better recall.
- Re-index on change events. Track freshness.

## 7. Feature availability by provider

Most Messages API features work on Bedrock, but beta features (some server tools, the Skills API, the Files API) can arrive later on Bedrock or not at all. List each feature the design depends on and verify it is available on the chosen provider before committing. This is the most common surprise when building on Bedrock.
