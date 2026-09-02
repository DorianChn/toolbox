"""LLM interface: classify a commit and extract a structured capsule.

Local-first: Ollama by default (http://localhost:11434). Any OpenAI-compatible
endpoint is supported via DEVCAPSULE_BASE_URL / DEVCAPSULE_API_KEY env vars.
Uses only the standard library (urllib) to avoid hard dependencies for MVP.
"""
from __future__ import annotations

import json
import os
import urllib.request

KINDS = {"bugfix", "feature", "refactor", "chore", "docs"}
CAPTURE_KINDS = {"bugfix", "feature"}  # only these become capsules by default

SYSTEM_PROMPT = (
    "You classify a git commit and extract a reusable engineering lesson. "
    "Respond ONLY with JSON, no markdown, no commentary."
)

EXTRACT_PROMPT = """Given a git commit subject and diff, do two things:

1. classify the commit into exactly one of: bugfix, feature, refactor, chore, docs
2. if it is bugfix or feature, extract a structured lesson with three fields, written
   in the SAME language as the commit subject (usually English or Chinese):
   - problem: one sentence, what was wrong or what was needed
   - solution: the concrete fix/approach, specific enough to reuse
   - gotcha: a pitfall or "do NOT do X" note, if any; else empty string

Respond with JSON in this exact shape:
{"kind": "<kind>", "problem": "...", "solution": "...", "gotcha": "...", "confidence": 0.0-1.0}

If the commit is chore/docs/refactor, set problem/solution/gotcha to empty strings.

Commit subject: {subject}

Diff (truncated):
{diff}
"""


class LLMError(Exception):
    pass


class LLM:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        from .config import get_setting

        self.base_url = (
            base_url
            or os.environ.get("DEVCAPSULE_BASE_URL")
            or get_setting("base_url")
            or "http://localhost:11434"
        ).rstrip("/")
        self.api_key = api_key or os.environ.get("DEVCAPSULE_API_KEY") or get_setting("api_key")
        # Two models: a small/fast one for *classifying* commits, and a larger
        # one for *extracting* the reusable lesson (problem/solution/gotcha).
        # Extraction quality is model-size dependent, so they can be split.
        self.model = os.environ.get("DEVCAPSULE_MODEL") or get_setting("model") or "qwen3:0.6b"
        self.extract_model = (
            os.environ.get("DEVCAPSULE_EXTRACT_MODEL")
            or get_setting("extract_model")
            or self.model
        )
        # API style: "ollama" (default) or "openai" (chat/completions)
        self.api_style = (
            os.environ.get("DEVCAPSULE_API_STYLE") or get_setting("api_style") or "ollama"
        )
        if self.api_key and self.api_style == "ollama":
            # an API key strongly implies an OpenAI-compatible host
            self.api_style = "openai"

    def _is_ollama(self) -> bool:
        return self.api_style == "ollama"

    def _post(self, path: str, payload: dict) -> dict:
        url = self.base_url + path
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        if self.api_key:
            req.add_header("Authorization", f"Bearer {self.api_key}")
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = resp.read().decode("utf-8")
        except Exception as e:
            raise LLMError(f"LLM request failed: {e}") from e
        return json.loads(body)

    def chat(self, user_prompt: str, model: str | None = None) -> str:
        model = model or self.model
        if self._is_ollama():
            payload = {
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "format": "json",
            }
            resp = self._post("/api/chat", payload)
            return resp.get("message", {}).get("content", "")
        # OpenAI-compatible /v1/chat/completions
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
        }
        resp = self._post("/v1/chat/completions", payload)
        return resp["choices"][0]["message"]["content"]

    def analyze_commit(self, subject: str, diff: str) -> dict:
        prompt = EXTRACT_PROMPT.replace("{subject}", subject).replace("{diff}", diff[:4000])
        text = self.chat(prompt, model=self.extract_model).strip()
        # strip accidental markdown fences
        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise LLMError(f"LLM returned invalid JSON: {e}\n{text[:200]}") from e
        kind = str(data.get("kind", "chore")).lower()
        if kind not in KINDS:
            kind = "chore"
        data["kind"] = kind
        data["confidence"] = float(data.get("confidence", 0.0))
        return data


def is_capture_kind(kind: str) -> bool:
    return kind in CAPTURE_KINDS
