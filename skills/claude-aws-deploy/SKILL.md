---
name: claude-aws-deploy
description: Deploy Claude-powered applications and their Agent Skills to AWS using Claude on Amazon Bedrock. Covers one-time deploy setup, Bedrock model access and IAM, containerising Agent SDK apps, infrastructure as code (ECS Fargate, Bedrock AgentCore Runtime or Lambda), CI/CD, staged rollout, smoke tests, monitoring and rollback, and publishing Skills through the right channel (baked into the app image, the Claude Skills API, claude.ai organisation skills, or a Claude Code plugin marketplace). Use whenever the user wants to deploy, host, ship, release, containerise, set up CI/CD for, monitor or roll back an AI app, agent or KAIRO module built on Claude, or wants to publish, version or distribute Claude skills to a team, even if they only say "put it on AWS" or "make it live".
---

# Claude on AWS: deploy apps and skills

Two different things get deployed, and they travel by different channels:

- **The application**: an Agent SDK or Messages API service. It runs as a container on AWS and calls Claude through Bedrock.
- **The Skills**: either baked into the application image, or published for people to use in claude.ai, Claude Code or the Claude API.

The flow borrows gstack's split: `/setup-deploy` records the deploy facts once; `/land-and-deploy` and `/canary` then ship and verify against them every time.

Never deploy to production, change IAM, or publish skills org-wide without the user's explicit go-ahead in the conversation. Show the plan (what changes, where, how to roll back) and wait.

AWS and Bedrock details change. Verify model availability per region, quotas and API names against current AWS and Anthropic docs before giving final commands.

## Step 0: Load or create the deploy config

Look for `DEPLOY.md` in the project root. If it exists, read it and skip to Step 2. If not, run Step 1.

If an `ARCHITECTURE.md` exists (from the `claude-app-architect` skill), read it for the runtime, provider, data classification and tool list.

## Step 1: One-time setup (writes DEPLOY.md)

Collect, asking only for what's missing:
- AWS account(s) per environment (dev, staging, prod), and the region;
- runtime target (see Step 2);
- IaC tool (Terraform or CDK) and CI system (GitHub Actions, GitLab, CodePipeline);
- how users authenticate (for KAIRO, Entra ID / Microsoft 365);
- connectivity to on-prem systems (VPN or Direct Connect to the GPU cluster, Jira, Git);
- which Skill channels are in use (Step 7);
- data residency rules.

Fill `assets/DEPLOY-template.md` and save it as `DEPLOY.md`. Later runs depend on it, so confirm it with the user.

## Step 2: Choose the runtime

| Target | Choose when | Watch out for |
|---|---|---|
| **ECS on Fargate** (default) | Web or API service, long agent sessions, streaming, MCP servers alongside | You manage scaling and session storage |
| **Bedrock AgentCore Runtime** | You want managed, session-isolated agent hosting with built-in identity and observability | Newer service: check region availability, limits and pricing |
| **Lambda** | Rung-1/2 workflows: single calls, short chains, event-driven jobs | 15-minute limit; poor fit for Agent SDK sessions |
| **EKS** | Only if the organisation already runs Kubernetes | Operational cost |

Agent SDK sessions run for minutes, spawn a subprocess and write files. That is why containers are the default. Lambda is for the Messages API only.

## Step 3: Bedrock foundation

Follow `references/bedrock-setup.md`: model access, inference profiles, the IAM policy (`assets/iam-bedrock-policy.json`), private networking, quotas, guardrails and invocation logging. Run `scripts/smoke_test.py --bedrock` before building anything on top. It proves credentials, region and model access in one call.

## Step 4: Package the app

Start from `assets/Dockerfile`:
- non-root user, pinned base image, health check;
- Skills copied into the image at `.claude/skills/`, so the image tag versions the app and its Skills together;
- no secrets in the image: everything sensitive comes from Secrets Manager at runtime;
- provider chosen by environment: `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_REGION`, and model IDs in env vars.

Run `scripts/validate_skills.py .claude/skills` in CI before building.

## Step 5: Infrastructure as code

Use Terraform or CDK. Never hand-build production in the console: it can't be reviewed, repeated or rolled back. The reference layout, sizing for about 150 users, and the KAIRO hybrid link are in `references/aws-infrastructure.md`.

## Step 6: CI/CD

Adapt `assets/github-actions-deploy.yml`. Its stages are:
1. test, then validate Skills;
2. build, image scan, push to ECR (tagged with the git SHA);
3. deploy to staging, then smoke test;
4. manual approval;
5. deploy to production, then smoke test and canary watch.

CI uses GitHub OIDC to assume an AWS role, so there are no long-lived keys.

## Step 7: Deploy the Skills

Pick the channel per audience. Details, commands and versioning are in `references/skills-channels.md`.

| Audience | Channel |
|---|---|
| The KAIRO app's own agents (Agent SDK on Bedrock) | Baked into the image (Step 4) |
| Apps calling the Claude API directly | Skills API (`/v1/skills`), with versions pinned |
| Staff using claude.ai | Organisation skills, provisioned by an admin |
| Engineers in Claude Code (IDE channel) | A private plugin marketplace in Git; Claude Code itself can run on Bedrock |

Package with `scripts/package_skills.sh`, which produces one zip per Skill.

## Step 8: Verify

After every deploy:
1. Run `scripts/smoke_test.py --url <env URL>`: health endpoint, plus one real prompt through the app to Bedrock.
2. Watch the canary for 15–30 minutes: 5xx rate, p95 latency, Bedrock throttling (`ThrottlingException`), token spend per task, and tool error rate.
3. Report to the user what was deployed (image tag, Skill versions), where it went, the smoke test result and the canary result.

## Step 9: Roll back

- **App**: redeploy the previous ECS task definition, or the previous image tag. Keep the last 3 known-good tags.
- **Skills API**: pin the previous version ID.
- **Plugin marketplace**: revert the commit or tag.
- **Infrastructure**: revert the IaC change and re-apply. Never hot-fix production state by hand.
