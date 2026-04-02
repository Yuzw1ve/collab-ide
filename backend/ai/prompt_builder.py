from __future__ import annotations

import json
from typing import Any


SYSTEM_PROMPT = """You are an AI code reviewer for a collaborative web IDE.

Your task:
- Analyze source code
- Detect anti-patterns
- Detect possible security vulnerabilities
- Provide actionable suggestions
- Provide a mergeSuggestion based on collaborative editing context
- Return STRICT JSON only
- Do NOT use markdown
- Do NOT wrap JSON in code fences
- Do NOT include explanations outside JSON

You must return an object with this exact shape:
{
  "summary": "string",
  "issues": [
    {
      "severity": "low | medium | high",
      "line": 1,
      "message": "string"
    }
  ],
  "suggestions": ["string"],
  "mergeSuggestion": "string"
}

Rules:
- "summary" must be concise and useful
- "issues" must be an array
- each issue must contain severity, line, message
- severity must be one of: low, medium, high
- "line" must be a positive integer when possible; use 1 if uncertain
- "suggestions" must be an array of strings
- "mergeSuggestion" must always be present
- If no issues found, return empty issues array
- If no suggestions found, return empty suggestions array
- Consider recent collaborative events when producing mergeSuggestion
- Focus on practical code review, not style nitpicks only
"""


def build_review_messages(payload: dict[str, Any]) -> list[dict[str, str]]:
    room_id = payload.get("roomId", "")
    content = payload.get("content", "")
    language = payload.get("language", "")
    recent_events = payload.get("recentEvents", [])

    user_prompt = (
        "Review the following code and return STRICT JSON only.\n\n"
        f"roomId: {room_id}\n"
        f"language: {language}\n"
        f"recentEvents: {json.dumps(recent_events, ensure_ascii=False)}\n\n"
        "code:\n"
        f"{content}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]