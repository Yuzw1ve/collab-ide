from __future__ import annotations

import json
import os
from typing import Any

import requests
from pydantic import BaseModel, Field, ValidationError

from .mock_review import generate_mock_review
from .prompt_builder import build_review_messages


class ReviewRequest(BaseModel):
    roomId: str = Field(..., min_length=1)
    content: str
    language: str = Field(..., min_length=1)
    recentEvents: list[dict[str, Any]] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    severity: str
    line: int = Field(..., ge=1)
    message: str


class ReviewResponse(BaseModel):
    summary: str
    issues: list[ReviewIssue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    mergeSuggestion: str


def _strip_json_fences(text: str) -> str:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def _extract_json_object(text: str) -> str:
    cleaned = _strip_json_fences(text)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end < start:
        return cleaned

    return cleaned[start:end + 1]


def _normalize_response(data: dict[str, Any]) -> dict[str, Any]:
    issues = data.get("issues", [])
    normalized_issues: list[dict[str, Any]] = []

    if isinstance(issues, list):
        for issue in issues:
            if not isinstance(issue, dict):
                continue

            severity = str(issue.get("severity", "low")).lower()
            if severity not in {"low", "medium", "high"}:
                severity = "low"

            line = issue.get("line", 1)
            try:
                line = int(line)
            except (TypeError, ValueError):
                line = 1
            if line < 1:
                line = 1

            message = str(issue.get("message", "Issue detected")).strip() or "Issue detected"

            normalized_issues.append(
                {
                    "severity": severity,
                    "line": line,
                    "message": message,
                }
            )

    suggestions = data.get("suggestions", [])
    if not isinstance(suggestions, list):
        suggestions = []

    normalized_suggestions = [str(item).strip() for item in suggestions if str(item).strip()]

    return {
        "summary": str(data.get("summary", "Review completed")).strip() or "Review completed",
        "issues": normalized_issues,
        "suggestions": normalized_suggestions,
        "mergeSuggestion": str(
            data.get("mergeSuggestion", "No merge conflicts detected")
        ).strip() or "No merge conflicts detected",
    }


def _call_llm(payload: ReviewRequest) -> dict[str, Any]:
    api_key = os.getenv("AI_REVIEWER_API_KEY", "").strip()
    endpoint = os.getenv("AI_REVIEWER_API_ENDPOINT", "").strip()
    model = os.getenv("AI_REVIEWER_MODEL", "gpt-4o-mini").strip()
    timeout_raw = os.getenv("AI_REVIEWER_TIMEOUT", "20").strip()

    if not api_key or not endpoint:
        raise RuntimeError("LLM configuration is missing")

    try:
        timeout = int(timeout_raw)
    except ValueError:
        timeout = 20

    messages = build_review_messages(payload.dict())

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    body = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }

    response = requests.post(endpoint, headers=headers, json=body, timeout=timeout)
    response.raise_for_status()

    raw = response.json()

    if isinstance(raw, dict):
        choices = raw.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content", "")
                    if isinstance(content, str) and content.strip():
                        parsed = json.loads(_extract_json_object(content))
                        return _normalize_response(parsed)

    raise RuntimeError("Unexpected LLM response format")


def review_code(payload: ReviewRequest | dict[str, Any]) -> dict[str, Any]:
    try:
        request_model = payload if isinstance(payload, ReviewRequest) else ReviewRequest(**payload)
    except ValidationError as exc:
        raise ValueError(f"Invalid review request payload: {exc}") from exc

    try:
        llm_result = _call_llm(request_model)
        validated = ReviewResponse(**llm_result)
        return validated.dict()
    except Exception:
        mock_result = generate_mock_review(request_model.dict())
        validated = ReviewResponse(**_normalize_response(mock_result))
        return validated.dict()