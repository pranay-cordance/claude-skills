# Bedrock foundation for Claude

Docs: https://docs.claude.com/en/api/claude-on-amazon-bedrock and https://code.claude.com/docs/en/amazon-bedrock (Agent SDK and Claude Code on Bedrock).

## 1. Model access
In the Bedrock console, open the model catalogue, select the Anthropic models you need, and submit the use-case details once per account (or once per AWS Organization). Do this in every account: dev, staging and prod.

## 2. Region and inference profiles
- Use **inference profile IDs** (cross-region profiles) rather than bare model IDs where AWS requires them. Profiles spread load across regions and raise effective throughput.
- **Data residency (India):** check whether the Claude models you need are offered in `ap-south-1` (Mumbai), and which regions each geographic inference profile (for example APAC) can route to. If policy requires processing inside India, confirm that the chosen profile satisfies it. If it doesn't, keep that data on the local SLMs.
- Write the decision into `DEPLOY.md`.

## 3. Configure the app
```bash
CLAUDE_CODE_USE_BEDROCK=1
AWS_REGION=<region>
ANTHROPIC_MODEL=<inference profile ID for the default model>
# Agent SDK / Claude Code also read variables for the small/fast model; see the Bedrock page for current names.
```
For Messages API code without the Agent SDK, use the Anthropic SDK's Bedrock client (`AnthropicBedrock`) or boto3 `bedrock-runtime` (`converse` / `invoke_model`).

## 4. IAM
- The task role gets `assets/iam-bedrock-policy.json`. Narrow `Resource` to the specific inference profiles and foundation models you use.
- Use separate roles for app tasks, CI and humans. Never use access keys inside containers.

## 5. Private networking
- Add VPC interface endpoints (PrivateLink) for `bedrock-runtime`, plus `ecr.api`, `ecr.dkr`, `logs`, `secretsmanager` and `sts`, and a gateway endpoint for S3. Traffic to Claude then never crosses the public internet.
- Tasks run in private subnets. Restrict any NAT egress to what MCP servers need.

## 6. Quotas and throughput
- Check the tokens-per-minute and requests-per-minute quotas for each model and region. For about 150 users with agent workloads, request increases before launch.
- Handle `ThrottlingException` with exponential backoff and jitter, and surface a "busy, retrying" state to the user.
- Consider provisioned throughput only after measuring steady load.

## 7. Guardrails and logging
- **Bedrock Guardrails** can add PII filters and denied topics as a second layer. Primary PII masking still happens in your code before the call.
- **Model invocation logging** (to S3 or CloudWatch) helps with audit. Prompts may contain sensitive data, so encrypt with KMS, restrict access and set retention.
- **Prompt caching** is supported for Claude on Bedrock. Check current specifics, and cache the system prompt and tool definitions.

## 8. Feature parity
Before deploying, list every Claude feature the app uses (from `ARCHITECTURE.md`) and confirm each one is available on Bedrock in your region. Beta features may lag.
