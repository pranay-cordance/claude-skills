# Deploying Skills: four channels

Every channel starts from the same source: one Git repo, `skills/<name>/SKILL.md`, validated in CI by `scripts/validate_skills.py`. Version the repo with tags; each channel deploys from a tag.

## 1. Baked into the app image (Agent SDK, including on Bedrock)
- In the Dockerfile, copy Skills to `<app dir>/.claude/skills/`.
- The app enables them with `setting_sources=["project"]` and the `Skill` tool in `allowed_tools`.
- **Versioning:** the image tag. Rollback means rolling back the image.
- Use this for the KAIRO app on Bedrock. It needs no Anthropic API key and no Skills API.

## 2. Claude Skills API (apps calling the Claude API directly)
Upload a Skill folder (it must have `SKILL.md` at its root) to `POST /v1/skills` with the Skills beta header. Add new versions to the same skill. Reference it in Messages requests through the `container` parameter together with the code-execution tool.

```bash
curl https://api.anthropic.com/v1/skills \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "display_title=requirements-to-stories" \
  -F "files[]=@skills/requirements-to-stories/SKILL.md;filename=requirements-to-stories/SKILL.md"
```

- In production, pin a **specific version**, not `latest`, so that a Skill change goes through the same release gate as code.
- Check the current docs for the beta header value, the versions endpoint, and the `container.skills` request shape: https://docs.claude.com/en/api/skills
- Check whether the Skills API is available on Bedrock before relying on it there. If it isn't, use channel 1.

## 3. claude.ai organisation skills (staff in the chat app)
- Team and Enterprise admins can provision Skills for the organisation. Users can also upload a Skill zip under Settings, which needs code execution enabled.
- Package with `scripts/package_skills.sh`, which produces one zip per Skill.
- Check the current admin flow at https://support.claude.com before writing steps for users.

## 4. Claude Code plugin marketplace (engineers in the IDE)
Put a marketplace in a private Git repo:

```
kairo-claude-plugins/
├── .claude-plugin/marketplace.json
└── plugins/
    └── kairo-engineering/
        ├── .claude-plugin/plugin.json
        └── skills/requirements-to-stories/SKILL.md
```

`marketplace.json`:
```json
{
  "name": "kairo",
  "owner": { "name": "KAIRO Platform Team" },
  "plugins": [
    { "name": "kairo-engineering", "source": "./plugins/kairo-engineering",
      "description": "KAIRO product & engineering skills" }
  ]
}
```

Engineers install it with `/plugin marketplace add <git-url>` and then `/plugin install kairo-engineering@kairo`. To require it for a repository, add it to that repo's `.claude/settings.json`.

Claude Code can run on Bedrock (`CLAUDE_CODE_USE_BEDROCK=1`), so the IDE channel also stays inside your AWS account. Check the plugin and marketplace docs for the current schema: https://code.claude.com/docs

## Release gate for Skills (all channels)
1. `validate_skills.py` passes.
2. The Skill's eval cases pass (from `claude-app-architect`: golden set per capability).
3. Changelog entry.
4. Tag.
5. Deploy to staging and smoke test.
6. Deploy to production with the user's approval.
