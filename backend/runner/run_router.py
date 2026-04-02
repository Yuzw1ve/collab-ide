from __future__ import annotations

import time
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .code_runner import run_code
from room_manager import room_manager


router = APIRouter(tags=["runner"])


class RunCodeRequest(BaseModel):
    roomId: str = Field(..., min_length=1, max_length=255)
    language: Literal["python", "javascript"]
    content: str = Field(..., min_length=0, max_length=50 * 1024)
    username: str = Field(..., min_length=1, max_length=255)


class RunCodeResponse(BaseModel):
    stdout: str
    stderr: str
    exitCode: int


class RunOutputEvent(BaseModel):
    type: str = "run_output"
    language: str
    stdout: str
    stderr: str
    exitCode: int
    username: str
    timestamp: int


class RunEvent(BaseModel):
    type: str = "run"
    username: str
    timestamp: int
    details: str


def build_run_output_event(
    *,
    language: str,
    stdout: str,
    stderr: str,
    exit_code: int,
    username: str,
) -> dict:
    return RunOutputEvent(
        language=language,
        stdout=stdout,
        stderr=stderr,
        exitCode=exit_code,
        username=username,
        timestamp=int(time.time()),
    ).dict()


def build_run_event(*, language: str, username: str) -> dict:
    return RunEvent(
        username=username,
        timestamp=int(time.time()),
        details=f"Ran {language} code",
    ).dict()


@router.post("/api/run", response_model=RunCodeResponse)
async def run_code_endpoint(payload: RunCodeRequest) -> RunCodeResponse:
    result = run_code(payload.language, payload.content)

    exit_code = int(result.get("exitCode", 1))

    # successful run = +3
    if exit_code == 0:
        await room_manager.award_points(payload.roomId, payload.username, 3)

    return RunCodeResponse(
        stdout=str(result.get("stdout", "")),
        stderr=str(result.get("stderr", "")),
        exitCode=exit_code,
    )