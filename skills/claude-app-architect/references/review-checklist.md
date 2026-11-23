# Architecture review checklist

Score each section 0–10. Below 7: state what a 10 looks like, then fix it or log it as an open decision.

## 1. Scope and value
- One wedge, with one measurable KPI and a baseline value
- Named pilot users; a clear definition of "done" for the pilot

## 2. Pattern fit
- Lowest rung that works (see SKILL.md, Phase 2); each agent and subagent justified
- Deterministic steps live in code, not in prompts

## 3. Data flow and trust boundaries
- Mermaid diagram from user to channel, orchestrator, subagent, tools and models, and back
- Each boundary marked: user, internal service, external system, model provider
- Every data source classified (public, internal, confidential, PII) with an allowed-model policy

## 4. Tools and actions
- Read and write tools separated; every write gated by human approval or an explicit policy
- Tools idempotent or safely retryable; timeouts set
- Per-role tool allowlists defined

## 5. Security
- Prompt-injection stance: tool output is data; no tool output can widen permissions
- Secrets in a secret manager, never in prompts, images or Skills
- End-user identity propagated to MCP servers and retrieval (no shared super-user)
- PII masking before external model calls, enforced in code

## 6. Failure modes
Table: failure, how it is detected, user-visible behaviour, recovery. Cover at least: model throttling or timeout, tool error, retrieval miss, hallucinated citation, runaway loop (cap turns and budget), partial write.

## 7. Evals and tests
- Golden set per capability, with an automatic grader where possible and human review otherwise
- Regression run on every prompt, Skill or model change
- Unit tests for tools and routing; an end-to-end smoke test

## 8. Cost and latency
- Tokens per task × tasks per day × price, per model tier; caching assumptions stated
- p50 and p95 latency targets; streaming to the user

## 9. Observability
- A per-task trace (model calls, tool calls, tokens, latency, outcome)
- KPI events defined; audit log retention set

## 10. Open decisions
Each with an owner and a date.
