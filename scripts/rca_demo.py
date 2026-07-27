#!/usr/bin/env python3
"""
Verified RCA demo — Apodex API (standalone CLI).

Loads a sanitized CDN incident + evidence fixture, sends it to the Apodex API
with a strict "cite every claim to an EVIDENCE-ID" contract, and renders the
resulting reasoning chain as:

    Hypothesis -> Evidence checked -> Conclusion -> Confidence

Uses raw httpx + manual SSE parsing (not the OpenAI SDK) because Apodex's
`reasoning_steps` delta field is dropped by the standard OpenAI SDK — manual
parsing is required to show the model's live "thinking" trace during the demo.
See ../../apodex/apodex/apodex.md for the full API reference this is built from.

Usage:
    cd sre-agent
    pip install -r requirements.txt
    export APODEX_API_KEY=sk-...      # or put it in .env
    python3 scripts/rca_demo.py
    python3 scripts/rca_demo.py --compare     # stretch: bare-LLM comparison + grounding score
    python3 scripts/rca_demo.py --no-stream   # skip live [thinking] trace, just print the result
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
FIXTURE_PATH = REPO_ROOT / "fixtures" / "cdn-incident.md"

load_dotenv(REPO_ROOT / ".env")

APODEX_BASE_URL = os.getenv("APODEX_BASE_URL", "https://api.apodex.ai/v1")
APODEX_MODEL = os.getenv("APODEX_MODEL", "apodex-1-0-deep-solve")

RCA_SYSTEM_PROMPT = """\
You are a Site Reliability Engineer performing root-cause analysis on a CDN \
incident. You will be given an incident description and a set of labeled \
evidence blocks (EVIDENCE-1, EVIDENCE-2, ...).

Rules:
- Investigate step by step: propose a hypothesis, check it against specific \
evidence, then state whether that hypothesis is confirmed, refuted, or \
partially supported.
- Every conclusion MUST cite the specific EVIDENCE-ID(s) it is based on. Do \
not state or assume any configuration behavior that is not shown in the \
provided evidence.
- If the evidence is insufficient to confirm a hypothesis, say so explicitly \
rather than guessing.
- After your narrative investigation, end your response with a fenced json \
code block containing ONLY a JSON array, no other text inside the fence, \
using exactly this schema:

```json
[
  {
    "hypothesis": "<string>",
    "evidence_checked": ["EVIDENCE-1", "EVIDENCE-2"],
    "conclusion": "<string>",
    "confidence": "low" | "medium" | "high"
  }
]
```
"""

NAIVE_SYSTEM_PROMPT = """\
You are a helpful assistant. Answer the user's question about their CDN \
incident directly and concisely.
"""

JUDGE_SYSTEM_PROMPT = """\
You are a strict grading assistant reviewing an AI's root-cause analysis of a \
CDN incident. You will be given the EVIDENCE that was available, and an \
ANSWER produced by a model. For each concrete factual claim the ANSWER makes \
about system/config behavior, decide whether it is:
  - "grounded": directly supported by the provided evidence
  - "fabricated": asserts specific config/system behavior not present in the \
evidence (even if it sounds plausible)
  - "unclear": too vague to classify

Respond ONLY with a JSON object:
{"grounded": <int>, "fabricated": <int>, "unclear": <int>, "notes": "<one or two sentences>"}
"""


def load_fixture() -> str:
    if not FIXTURE_PATH.exists():
        print(f"ERROR: fixture not found at {FIXTURE_PATH}", file=sys.stderr)
        sys.exit(1)
    return FIXTURE_PATH.read_text()


def build_rca_messages(fixture_text: str) -> list[dict]:
    return [
        {"role": "system", "content": RCA_SYSTEM_PROMPT},
        {"role": "user", "content": fixture_text},
    ]


def extract_incident_only(fixture_text: str) -> str:
    """Strip the '## Evidence' and '## What a well-grounded RCA should conclude'
    sections, leaving just the incident description — used for the naive
    (ungrounded) comparison call, so it has the problem but not the evidence."""
    marker = "## Evidence"
    idx = fixture_text.find(marker)
    return fixture_text[:idx].strip() if idx != -1 else fixture_text


def stream_chat_completion(api_key: str, messages: list[dict], show_thinking: bool) -> str:
    """POST /v1/chat/completions with stream=true, manually parse SSE frames.

    Returns the concatenated final `content` text. If show_thinking is True,
    prints [thinking]/[tool] reasoning_steps live and streams content tokens
    to stdout as they arrive.
    """
    url = f"{APODEX_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {"model": APODEX_MODEL, "messages": messages, "stream": True}

    content_parts: list[str] = []

    with httpx.Client(timeout=300.0) as client:
        with client.stream("POST", url, headers=headers, json=body) as resp:
            if resp.status_code != 200:
                resp.read()
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")

            buffer = ""
            for chunk in resp.iter_text():
                buffer += chunk
                lines = buffer.split("\n")
                buffer = lines.pop()  # keep incomplete line for next chunk

                for line in lines:
                    if not line or line.startswith(":"):
                        continue  # blank line / SSE heartbeat comment
                    if not line.startswith("data: "):
                        continue
                    payload = line[len("data: "):]
                    if payload == "[DONE]":
                        continue

                    try:
                        frame = json.loads(payload)
                    except json.JSONDecodeError:
                        continue

                    choice = (frame.get("choices") or [{}])[0]
                    delta = choice.get("delta") or {}

                    for step in delta.get("reasoning_steps") or []:
                        if show_thinking:
                            step_type = step.get("type", "reasoning")
                            if step_type == "thinking":
                                print(f"\n[thinking] {step.get('thought', '')}", flush=True)
                            else:
                                print(f"\n[{step_type}] {json.dumps(step, ensure_ascii=False)}", flush=True)

                    text = delta.get("content")
                    if text:
                        content_parts.append(text)
                        if show_thinking:
                            print(text, end="", flush=True)

                    if choice.get("finish_reason") == "error":
                        err = frame.get("error") or {}
                        raise RuntimeError(f"Apodex workflow error: {err}")

    if show_thinking:
        print()  # trailing newline after streamed content
    return "".join(content_parts)


def call_naive_llm(api_key: str, question: str) -> str:
    """Bare comparison call: no evidence, no format contract, non-streaming."""
    url = f"{APODEX_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": APODEX_MODEL,
        "messages": [
            {"role": "system", "content": NAIVE_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }
    resp = httpx.post(url, headers=headers, json=body, timeout=300.0)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def judge_grounding(api_key: str, evidence_text: str, answer: str) -> dict:
    url = f"{APODEX_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": APODEX_MODEL,
        "messages": [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": f"EVIDENCE:\n{evidence_text}\n\nANSWER:\n{answer}"},
        ],
        "stream": False,
    }
    resp = httpx.post(url, headers=headers, json=body, timeout=300.0)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"grounded": 0, "fabricated": 0, "unclear": 0, "notes": f"unparseable judge output: {raw}"}


def extract_reasoning_chain(answer_text: str) -> list[dict] | None:
    """Pull the trailing ```json ... ``` block out of the model's answer."""
    matches = re.findall(r"```json\s*(.*?)\s*```", answer_text, flags=re.DOTALL)
    if not matches:
        return None
    try:
        parsed = json.loads(matches[-1])
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    return parsed


CONFIDENCE_ICON = {"high": "\u25cf\u25cf\u25cf", "medium": "\u25cf\u25cf\u25cb", "low": "\u25cf\u25cb\u25cb"}


def render_chain(steps: list[dict]) -> str:
    lines = []
    for i, step in enumerate(steps, 1):
        conf = str(step.get("confidence", "unknown")).lower()
        icon = CONFIDENCE_ICON.get(conf, "???")
        evidence = ", ".join(step.get("evidence_checked") or []) or "(none cited)"
        lines.append(f"── Step {i} " + "─" * max(1, 50 - len(f"Step {i}")))
        lines.append(f"  Hypothesis:       {step.get('hypothesis', '')}")
        lines.append(f"  Evidence checked: {evidence}")
        lines.append(f"  Conclusion:       {step.get('conclusion', '')}")
        lines.append(f"  Confidence:       {icon} ({conf})")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Verified RCA demo against the Apodex API.")
    parser.add_argument("--compare", action="store_true",
                         help="Also run a bare/ungrounded LLM call on the same incident and grade grounding.")
    parser.add_argument("--no-stream", action="store_true",
                         help="Don't print live [thinking] trace; just show the final chain.")
    args = parser.parse_args()

    api_key = os.getenv("APODEX_API_KEY")
    if not api_key:
        print("ERROR: APODEX_API_KEY is not set (env var or sre-agent/.env).", file=sys.stderr)
        sys.exit(1)

    fixture_text = load_fixture()

    print(f"=== Verified RCA — model: {APODEX_MODEL} ===\n")
    print("Running grounded investigation (incident + evidence)...\n")

    messages = build_rca_messages(fixture_text)
    answer = stream_chat_completion(api_key, messages, show_thinking=not args.no_stream)

    chain = extract_reasoning_chain(answer)
    print("\n" + "=" * 60)
    if chain:
        print(f"REASONING CHAIN ({len(chain)} step(s)):\n")
        print(render_chain(chain))
    else:
        print("WARNING: could not extract a structured reasoning chain from the response.")
        print("Raw answer:\n")
        print(answer)

    if not args.compare:
        return

    print("=" * 60)
    print("\n=== Comparison: ungrounded (no evidence) bare LLM call ===\n")
    naive_question = extract_incident_only(fixture_text)
    naive_answer = call_naive_llm(api_key, naive_question)
    print(naive_answer)

    print("\n--- Grading grounding: verified vs. naive ---\n")
    evidence_only = fixture_text[fixture_text.find("## Evidence"):]

    verified_verdict = judge_grounding(api_key, evidence_only, answer)
    naive_verdict = judge_grounding(api_key, evidence_only, naive_answer)

    def score(v: dict) -> str:
        total = v.get("grounded", 0) + v.get("fabricated", 0) + v.get("unclear", 0)
        pct = (100 * v.get("grounded", 0) / total) if total else 0
        return f"{v.get('grounded', 0)}/{total} claims grounded ({pct:.0f}%) — {v.get('notes', '')}"

    print(f"Verified (Apodex, evidence-grounded): {score(verified_verdict)}")
    print(f"Naive    (bare LLM, no evidence):     {score(naive_verdict)}")


if __name__ == "__main__":
    main()
