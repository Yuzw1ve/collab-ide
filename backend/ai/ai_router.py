from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .ai_reviewer import ReviewRequest, ReviewResponse, review_code
from telegram_notifier import send_telegram_message

router = APIRouter(tags=["ai-reviewer"])


@router.post("/api/ai/review", response_model=ReviewResponse)
def review_code_endpoint(payload: ReviewRequest) -> ReviewResponse:
    try:
        result = review_code(payload)

        issues = result.get("issues", [])
        has_high_severity = any(
            isinstance(issue, dict) and issue.get("severity") == "high"
            for issue in issues
        )

        if has_high_severity:
            send_telegram_message(
                f"⚠️ High severity AI issue detected in room {payload.roomId}"
            )

        return ReviewResponse(**result)

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AI review failed") from exc