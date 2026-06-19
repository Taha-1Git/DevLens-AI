from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import httpx

app = FastAPI(title="DevLens AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-haiku-4-5-20251001"  # fastest + cheapest, still very good
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class Chunk(BaseModel):
    path: str
    content: str


class AskRequest(BaseModel):
    question: str
    chunks: List[Chunk]
    all_paths: Optional[List[str]] = []


class SummaryRequest(BaseModel):
    summary_type: str  # full | stack | flow | readme | security
    chunks: List[Chunk]
    all_paths: Optional[List[str]] = []


SUMMARY_PROMPTS = {
    "full": "Provide a full project summary: 1) Purpose & overview 2) Tech stack & frameworks 3) Main modules and their roles 4) Folder structure 5) Key files explained 6) How to install and run the project.",
    "stack": "List ALL technologies, frameworks, libraries, and tools used. Group by: Frontend, Backend, Database, DevOps/Infra, Testing. Include version numbers if visible in config files.",
    "flow": "Trace the main code execution flow step by step from entry point to response: start → routing → middleware → business logic → data layer → response. Include actual file names at each step.",
    "readme": "Write a complete, professional README.md with: project title, description, features list, tech stack, prerequisites, installation steps, usage examples, API endpoints (if any), environment variables, and contributing guidelines.",
    "security": "Perform a security audit. Look for: hardcoded secrets or API keys, SQL injection risks, missing authentication/authorization, exposed sensitive endpoints, insecure dependencies, missing input validation, CORS misconfig, insecure file handling. Be specific with file names and code context.",
}


async def call_claude(system_prompt: str, user_message: str) -> str:
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set on server.")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1500,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(ANTHROPIC_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        return data["content"][0]["text"]


def build_context(chunks: List[Chunk], all_paths: List[str]) -> str:
    file_list = "\n".join(all_paths[:80]) if all_paths else ""
    code_ctx = "\n\n".join(
        f"File: {c.path}\n```\n{c.content[:800]}\n```" for c in chunks[:8]
    )
    return f"Project files ({len(all_paths)} total):\n{file_list}\n\nRelevant code:\n{code_ctx}"


@app.get("/")
def root():
    return {"status": "DevLens AI backend running", "model": CLAUDE_MODEL}


@app.get("/health")
def health():
    return {"ok": True, "key_set": bool(ANTHROPIC_API_KEY)}


@app.post("/ask")
async def ask(req: AskRequest):
    system = (
        "You are DevLens AI, a senior software engineer helping developers understand codebases. "
        "Answer using ONLY the code context provided. Be concise and technical. "
        "Mention specific file names. Use markdown code blocks for code snippets. "
        "If context is insufficient, say so and suggest which files to check."
    )
    context = build_context(req.chunks, req.all_paths)
    user_msg = f"Question: {req.question}\n\n{context}"
    answer = await call_claude(system, user_msg)
    paths = list({c.path for c in req.chunks})
    return {"answer": answer, "sources": paths}


@app.post("/summary")
async def summary(req: SummaryRequest):
    prompt = SUMMARY_PROMPTS.get(req.summary_type, SUMMARY_PROMPTS["full"])
    system = (
        "You are DevLens AI, a senior software engineer. "
        "Analyze the provided codebase context thoroughly. "
        "Be detailed, well-structured, and use markdown formatting."
    )
    context = build_context(req.chunks, req.all_paths)
    user_msg = f"{prompt}\n\n{context}"
    answer = await call_claude(system, user_msg)
    return {"answer": answer, "type": req.summary_type}
