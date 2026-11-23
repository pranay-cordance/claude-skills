# KAIRO capability service (scaffold)

A FastAPI service that runs a Claude Agent SDK orchestrator with:
- one capability subagent (`engineering`) using a project Skill;
- an in-process MCP tool (`create_story_draft`) that needs human approval;
- model and provider settings read from environment variables.

First rename `.claude/skills/*/SKILL.md.template` to `SKILL.md`.

Run locally:

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=...            # or: CLAUDE_CODE_USE_BEDROCK=1 and AWS_REGION=...
    uvicorn app.main:app --reload

Check the current Agent SDK docs before extending; option names can change between releases.
Deploy with the `claude-aws-deploy` skill.
