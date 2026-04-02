from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


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
    type: Literal["run_output"] = "run_output"
    language: str
    stdout: str
    stderr: str
    exitCode: int
    username: str
    timestamp: int


class RunEvent(BaseModel):
    type: Literal["run"] = "run"
    username: str
    timestamp: int
    details: str