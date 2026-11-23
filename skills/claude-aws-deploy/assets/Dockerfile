# Agent SDK app image. Pin the base image digest in production.
FROM python:3.12-slim

# Node.js: recent claude-agent-sdk wheels bundle the agent CLI. If your version
# doesn't, keep Node and install the CLI as the SDK docs describe.
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 app
WORKDIR /srv/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
# Skills ship with the app: the image tag versions both together.
COPY .claude/skills/ ./.claude/skills/

ENV CLAUDE_CODE_USE_BEDROCK=1 \
    KAIRO_PROJECT_DIR=/srv/app \
    KAIRO_WORKSPACE_ROOT=/tmp/kairo-sessions \
    PYTHONUNBUFFERED=1
# AWS_REGION, ANTHROPIC_MODEL and secrets are injected by the ECS task definition.

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
