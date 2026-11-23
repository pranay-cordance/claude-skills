# Deploy configuration: <app name>

Written once by the claude-aws-deploy skill, then reused by every deploy. Keep it in Git and change it through review.

## Environments
| Env | AWS account | Region | URL | Approver |
|---|---|---|---|---|
| dev | | | | |
| staging | | | | |
| prod | | | | <name> |

## Runtime
- Target: ECS Fargate / AgentCore Runtime / Lambda
- IaC: Terraform / CDK (path: )
- CI: GitHub Actions / GitLab / CodePipeline
- Container registry: ECR repo
- Service / cluster names:

## Claude on Bedrock
- Default model (inference profile ID):
- Light model:
- Escalation model:
- Residency decision (region / profile and the reason):
- Quotas confirmed (TPM / RPM):

## Identity and network
- User auth: Entra ID via ALB OIDC / Cognito
- Hybrid link: VPN / Direct Connect to
- VPC endpoints in place: bedrock-runtime, ecr, logs, secretsmanager, sts, s3

## Skills channels
- [ ] Baked into the image (path: .claude/skills)
- [ ] Skills API (workspace, pinned versions)
- [ ] claude.ai organisation skills (admin)
- [ ] Claude Code plugin marketplace (repo URL)

## Verification
- Health URL:
- Smoke prompt:
- Canary window and alarm names:

## Rollback
- Previous good image tags:
- Command / runbook link:
