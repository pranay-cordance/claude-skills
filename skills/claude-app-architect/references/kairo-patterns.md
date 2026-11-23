# Mapping KAIRO GPT to Claude primitives

| KAIRO layer (diagram) | Claude-side design |
|---|---|
| End users (150) + access channels | Thin channel adapters (web UI, Teams bot, REST API). The IDE channel uses Claude Code with the same MCP servers and a KAIRO plugin of Skills |
| KAIRO orchestrator | Agent SDK orchestrator: intent classification (Haiku or a local SLM) chooses a capability subagent; policy hooks are global |
| KAIRO Consult / Product Intelligence | Subagent `consult`. Skills: idea-evaluation, feedback-theme-analysis, market-sizing, competitive-positioning. Tools: CRM/support read, knowledge search, web search |
| KAIRO Product & Engineering | Subagent `engineering`. Skills: requirements-to-stories, code-to-docs (functional, technical, DFD), test-generation, cloud-cost-review. Tools: Jira/Coda, Git (read; PRs behind approval), SharePoint publish (behind approval), SAST/DAST results |
| KAIRO Go-to-Market | Subagent `gtm`. Skills: pricing-analysis, pipeline-prioritisation, cross-sell-signals. Tools: CRM/ERP read, Snowflake (read-only views) |
| Shared support capabilities | Shared MCP servers (support, infrastructure, knowledge) used by all three subagents |
| Cordance context layer | One MCP server per source plus a retrieval service exposed as `search_knowledge`. "Domain semantics" becomes domain-glossary Skills per business unit |
| Model routing | Router in code: local SLM for PII masking, classification and simple extraction; Haiku for light steps; Sonnet as the agent default; Opus for escalation (complex reasoning, multi-step planning). Escalation triggers are explicit: eval-known hard task types, low-confidence signals, user request |
| Base LLM layer / external LLMs | On Bedrock, Claude runs within your AWS account boundary under IAM, which changes the "external, optional" box into a governed path. Keep local SLMs for on-prem-only data |
| Enterprise controls | RBAC means per-role `allowed_tools` and MCP OAuth. Human-in-the-loop uses the `can_use_tool` callback for every write. Audit uses hook-logged tool calls. PII is masked before egress. Residency is handled by region and inference-profile choice |
| KPI dashboard | Emit an event per task (capability, model, tokens, latency, outcome, human edits) and derive the KPIs from it, such as cycle time, cost per successful workflow and defect leakage |

## Phased roadmap

Recommended wedge: **Product & Engineering → requirements-to-stories in Jira.** It needs one data source (Jira/Coda), its write action is a draft for human approval, and it maps straight onto the "engineering cycle time" KPI.

1. **Wedge (4–6 weeks).** One subagent, two or three Skills, the Jira MCP, human approval on create, an eval set of 30 real requirements, and 10–20 pilot users.
2. **Context.** Add the retrieval service, Git and SharePoint MCPs, and code-to-docs.
3. **Breadth.** Add the Consult and GTM subagents, reusing the context layer.
4. **Optimise.** Model-routing tuning from eval data, local-SLM offload, the cost dashboard.

## Watch-outs specific to KAIRO

- **Code and customer data in prompts.** Decide per source whether it may reach Claude (Bedrock) or must stay on local SLMs. Write the decision into config, not into the prompt.
- **"Assess commercial viability" and "pricing" outputs** are advice. Label them clearly and keep a human owner for every decision.
- **Teams/SharePoint integration** needs Entra ID app registration and Graph permissions scoped narrowly.
