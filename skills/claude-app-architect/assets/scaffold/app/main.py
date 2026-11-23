from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .agent import run

app = FastAPI(title="KAIRO capability service")


class Ask(BaseModel):
    prompt: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/ask")
async def ask(body: Ask):
    # Authenticate the caller (e.g. Entra ID via the load balancer) before this point.
    async def stream():
        async for message in run(body.prompt):
            yield f"{message!r}\n"
    return StreamingResponse(stream(), media_type="text/plain")
