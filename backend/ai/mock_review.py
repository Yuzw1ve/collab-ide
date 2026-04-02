from __future__ import annotations

import re
from typing import Any


def _line_number(content: str, needle: str) -> int:
    lines = content.splitlines() or [content]
    for idx, line in enumerate(lines, start=1):
        if needle in line:
            return idx
    return 1


def _detect_bare_except(content: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        if re.match(r"^except\s*:\s*$", stripped):
            issues.append(
                {
                    "severity": "medium",
                    "line": idx,
                    "message": "Bare except detected; it may hide unexpected errors.",
                }
            )
        elif re.match(r"^catch\s*\([^)]*\)\s*\{\s*$", stripped):
            # Check next few lines for suspiciously empty catch block
            next_lines = lines[idx : min(idx + 3, len(lines))]
            joined = "\n".join(next_lines).strip()
            if joined.startswith("}") or joined == "":
                issues.append(
                    {
                        "severity": "medium",
                        "line": idx,
                        "message": "Catch block may be swallowing errors without handling.",
                    }
                )

    return issues


def _has_two_user_edits_in_a_row(recent_events: list[Any]) -> bool:
    normalized: list[str] = []

    for event in recent_events:
        if not isinstance(event, dict):
            continue

        event_type = str(event.get("type", "")).lower()
        user_id = (
            event.get("userId")
            or event.get("user")
            or event.get("author")
            or event.get("username")
        )

        if not user_id:
            continue

        if "edit" in event_type or "change" in event_type or "update" in event_type:
            normalized.append(str(user_id))

    if len(normalized) < 2:
        return False

    for i in range(len(normalized) - 1):
        if normalized[i] != normalized[i + 1]:
            return True

    return False


def generate_mock_review(payload: dict[str, Any]) -> dict[str, Any]:
    content = str(payload.get("content", "") or "")
    recent_events = payload.get("recentEvents", []) or []

    issues: list[dict[str, Any]] = []
    suggestions: list[str] = []

    if "eval(" in content:
        issues.append(
            {
                "severity": "high",
                "line": _line_number(content, "eval("),
                "message": "Use of eval detected; this may introduce severe security risks.",
            }
        )
        suggestions.append("Avoid eval and use safer parsing or explicit dispatch logic.")

    if "exec(" in content:
        issues.append(
            {
                "severity": "high",
                "line": _line_number(content, "exec("),
                "message": "Use of exec detected; executing dynamic code is a major security risk.",
            }
        )
        suggestions.append("Avoid exec and refactor to explicit function calls or safe interpreters.")

    if "console.log" in content:
        issues.append(
            {
                "severity": "low",
                "line": _line_number(content, "console.log"),
                "message": "Debug logging detected in production code.",
            }
        )
        suggestions.append("Consider removing console.log statements before merging.")

    if "print(" in content:
        issues.append(
            {
                "severity": "low",
                "line": _line_number(content, "print("),
                "message": "Debug print detected.",
            }
        )
        suggestions.append("Consider removing debug prints or replacing them with structured logging.")

    if "debugger" in content:
        issues.append(
            {
                "severity": "medium",
                "line": _line_number(content, "debugger"),
                "message": "Debugger statement detected; it may interrupt execution in development environments.",
            }
        )
        suggestions.append("Remove debugger statements before merging.")

    issues.extend(_detect_bare_except(content))

    if "except:" in content:
        suggestions.append("Handle specific exceptions instead of using a bare except clause.")

    if "catch" in content and ("catch {" in content or "catch(" in content):
        suggestions.append("Ensure caught exceptions are logged or handled explicitly.")

    stripped = content.strip()
    line_count = len([line for line in content.splitlines() if line.strip()])

    if len(stripped) < 20 or line_count <= 1:
        summary = "Code is minimal"
    elif not issues:
        summary = "No major issues detected"
    else:
        high_count = sum(1 for issue in issues if issue["severity"] == "high")
        if high_count > 0:
            summary = "Potential security and code quality issues detected"
        else:
            summary = "Some code quality issues detected"

    if _has_two_user_edits_in_a_row(recent_events):
        merge_suggestion = (
            "Possible merge conflict risk detected due to consecutive edits from different users."
        )
    else:
        merge_suggestion = "No merge conflicts detected"

    # Deduplicate suggestions while preserving order
    seen: set[str] = set()
    deduped_suggestions: list[str] = []
    for suggestion in suggestions:
        if suggestion not in seen:
            seen.add(suggestion)
            deduped_suggestions.append(suggestion)

    return {
        "summary": summary,
        "issues": issues,
        "suggestions": deduped_suggestions,
        "mergeSuggestion": merge_suggestion,
    }