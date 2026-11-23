# Claude Skills

Two Agent Skills for building enterprise AI applications on Claude, written for the KAIRO GPT platform and usable for any Claude-powered app.

| Skill | What it does |
|---|---|
| [`claude-app-architect`](skills/claude-app-architect/SKILL.md) | Turns an idea into a reviewed architecture: frames the job, picks the simplest pattern (single call, workflow, agent or multi-agent), designs the layers (Agent SDK, MCP, Skills, RAG, model routing, controls), runs a scored review, and writes `ARCHITECTURE.md` plus starter code |
| [`claude-aws-deploy`](skills/claude-aws-deploy/SKILL.md) | Deploys the app and its skills to AWS with Claude on Amazon Bedrock: one-time `DEPLOY.md` setup, Bedrock and IAM, container, infrastructure as code, CI/CD, smoke tests, canary watch and rollback; publishes skills by image, Skills API, claude.ai or plugin marketplace |

They are designed to be used in sequence: architect first, then deploy.

## Install

**Claude Code (recommended for engineers)**

```
/plugin marketplace add pranay-cordance/claude-skills
/plugin install claude-skills@cordance-claude-skills
```

**claude.ai**: download a zip from [`dist/`](dist/), then go to Settings → Capabilities → Skills and upload it. This needs a paid plan with code execution enabled. Team and Enterprise admins can also provision skills for the whole organisation.

**Manual**: copy a folder from `skills/` into `~/.claude/skills/` (for all your projects) or into `.claude/skills/` (for one project).

## Try it

- "Architect KAIRO's Go-to-Market module on Claude."
- "Design an agent that turns requirements into Jira user stories, with human approval."
- "Deploy the requirements-to-stories service to AWS staging using Bedrock."
- "Publish our skills to the team through a plugin marketplace."

## Repository layout

```
.claude-plugin/          Claude Code plugin + marketplace manifests
skills/
  claude-app-architect/  SKILL.md, references/, assets/ (ARCHITECTURE template, starter scaffold)
  claude-aws-deploy/     SKILL.md, references/, scripts/, assets/ (Dockerfile, CI, IAM, DEPLOY template)
dist/                    One zip per skill, for claude.ai upload or the Skills API
```

## Contributing

1. Edit the skill under `skills/`.
2. Run `python skills/claude-aws-deploy/scripts/validate_skills.py skills` (CI runs this too).
3. Rebuild the zips with `skills/claude-aws-deploy/scripts/package_skills.sh skills dist`.
4. Bump `version` in `.claude-plugin/plugin.json` and open a pull request.

Claude API, Agent SDK and Bedrock details change quickly. Both skills tell Claude to check the current docs, and fixes to the reference files are welcome.
