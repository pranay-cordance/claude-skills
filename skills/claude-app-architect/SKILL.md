---
name: claude-app-architect
description: Architect and scaffold enterprise AI applications on Claude (agents, tool use, MCP servers, Agent Skills, RAG, human-in-the-loop and model routing) using the Claude API, the Claude Agent SDK, or Claude on Amazon Bedrock. Use whenever the user wants to design, plan, build, structure or review an AI app, agent, copilot, assistant or internal "GPT" on Claude (for example KAIRO GPT modules for product intelligence, engineering delivery or go-to-market), asks which Claude building blocks to use, how to combine agents, tools, MCP and retrieval, how to route between Claude models and local SLMs, or wants an architecture document or starter code, even if they never say "architecture".
---

# Claude App Architect

Turns an idea for a Claude-powered application into a reviewed architecture and a runnable starting point. The output is an `ARCHITECTURE.md` built from `assets/ARCHITECTURE-template.md`, and, if the user wants code, a project copied from `assets/scaffold/`.

The method borrows from gstack's `/office-hours` (challenge the framing, find the narrowest useful wedge) and `/plan-eng-review` (force data flow, failure modes and tests into the open before code).

Product facts drift: model IDs, beta headers and SDK signatures change. Before writing code, check the current docs linked in `references/building-blocks.md`. Keep model IDs in config, never hardcoded from memory.

## Phase 1: Frame the job

Ask only what the conversation hasn't answered, one or two questions at a time:

1. **Who uses it, and where?** Roles, headcount, channel (web, IDE, Teams, API).
2. **What job, and how will we know it worked?** One use case and one measurable outcome, such as "requirement-to-story time drops from 3 days to 4 hours".
3. **What data does it read?** Sources, sensitivity (PII, customer data, source code) and residency rules.
4. **What does it change?** Any action with side effects: writing to Jira, sending a message, committing code.
5. **What are the constraints?** Latency, budget per task, cloud, which models are allowed.

Push back on scope. If the user describes a whole platform (all of KAIRO), propose a first wedge: one capability, one data source, one measurable KPI. Explain why: a narrow wedge produces real usage data and an eval set within weeks, and that data decides the rest of the platform better than any upfront design.

## Phase 2: Pick the lightest pattern that works

| Rung | Pattern | Use when | Built with |
|---|---|---|---|
| 1 | Single call + structured output | Extraction, classification, summarising one input | Messages API |
| 2 | Workflow (chain, route, parallelise) | Steps are known in advance | Your code calling the Messages API |
| 3 | Single agent with tools | Steps depend on what the model finds | Agent SDK, or a tool-use loop |
| 4 | Orchestrator + subagents | Distinct capabilities needing separate context, tools or permissions | Agent SDK subagents |

Climb a rung only when the lower one fails a requirement you can name. Each rung adds latency, cost, nondeterminism and test difficulty. Many "agent" ideas are really rung-2 workflows.

Then pick the runtime:

- **Agent SDK.** Default for rungs 3–4. It provides the agent loop, file and shell tools, MCP, Skills, subagents, hooks and permissions.
- **Messages API directly.** For rungs 1–2, or when you need full control of the loop.
- **Provider.** Anthropic API, or Amazon Bedrock (same SDK, configured by environment variables). The provider is a deployment choice and should not change app code; `claude-aws-deploy` handles it.

Details and code shapes for each primitive are in `references/building-blocks.md`.

## Phase 3: Design the layers

Use this seven-layer reference model. It mirrors the KAIRO GPT diagram, so KAIRO work maps one-to-one. `references/kairo-patterns.md` has the full mapping and a phased roadmap.

1. **Channels.** Web UI, IDE, Teams/SharePoint, API. Keep them thin: authenticate, then forward to the orchestrator.
2. **Orchestrator.** Classifies intent, picks a capability, enforces policy.
3. **Capabilities.** One subagent per bounded capability, each with its own system prompt, Skills and tool allowlist.
4. **Context layer.** MCP servers for live systems; a retrieval service for documents.
5. **Model routing.** Chooses the cheapest model tier that passes evals for each step.
6. **Model providers.** Claude (API or Bedrock), plus local SLMs where policy or cost requires.
7. **Controls and observability.** Cross-cutting: auth, RBAC, human-in-the-loop, audit, evals, cost.

Design rules, with the reason for each:

- **Put each kind of knowledge where it belongs.** Procedures and house style go in **Skills**: they load only when relevant, so they cost little context. Access to live systems goes in **MCP servers**, which are reusable across agents and clients, including the IDE. Large or changing document sets go in **retrieval**, so the model sees fresh, cited facts instead of stale prompt text.
- **Keep tools few and sharp.** Use clear names, typed inputs and outputs that say what happened. Split read tools from write tools. Gate write tools behind human approval, using permission callbacks or `PreToolUse` hooks. Approval belongs where the side effect happens, not in the prompt.
- **Treat everything a tool returns as untrusted data.** Documents, tickets, emails and web pages can contain prompt injections. Never let tool output widen permissions, add recipients or trigger write actions without the user.
- **Spend context deliberately.** Cache stable prefixes (system prompt, tool definitions). Retrieve instead of stuffing. Have subagents return summaries rather than raw dumps.
- **Route on evidence.** Start each step on a mid-tier model, build an eval set, then move steps down a tier where scores hold and up where they don't. PII masking and on-prem-only data happen before any external call, enforced in code.
- **Write evals before scaling.** Each capability gets a golden set of 20–50 real cases, graded automatically where possible. This set is what makes model upgrades and prompt changes safe.

## Phase 4: Review the design

Work through `references/review-checklist.md`. Its outputs are:

- a Mermaid data-flow diagram from user request to model and tools and back, marking trust boundaries;
- a failure-modes table (what breaks, how it is detected, what the user sees);
- an eval and test plan;
- a cost estimate per task and per month, based on tokens per task multiplied by volume;
- a list of open decisions, each with an owner.

Score each checklist section 0–10. For anything below 7, say what a 10 looks like and either fix the design or record it as an open decision. Don't paper over gaps.

## Phase 5: Write the document and scaffold

1. Fill `assets/ARCHITECTURE-template.md` and save it as `ARCHITECTURE.md` in the user's project, or deliver it as a document.
2. If the user wants code, copy `assets/scaffold/` and rename every `SKILL.md.template` to `SKILL.md` (stored that way so this skill doesn't contain a nested skill). Then adapt it. The scaffold is a FastAPI service that runs an Agent SDK orchestrator, with an example in-process MCP tool gated by approval, a project Skill, and a provider-agnostic model config. Replace the example capability with the user's wedge. Keep the structure.
3. Hand off: for deployment to AWS (the app and its Skills), use the `claude-aws-deploy` skill. It reads `ARCHITECTURE.md`.
