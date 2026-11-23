from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Model IDs come from the environment. On Bedrock, use inference profile IDs
    # from the Bedrock console; never hardcode them here.
    default_model: str = "sonnet"     # alias the SDK resolves; override per environment
    max_turns: int = 12               # caps runaway agent loops
    workspace_root: str = "/tmp/kairo-sessions"
    project_dir: str = "."            # contains .claude/skills

    class Config:
        env_prefix = "KAIRO_"


settings = Settings()
