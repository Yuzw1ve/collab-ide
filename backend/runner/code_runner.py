from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Dict


MAX_CODE_SIZE_BYTES = 50 * 1024  # 50KB
MAX_OUTPUT_SIZE_BYTES = 10 * 1024  # 10KB
RUN_TIMEOUT_SECONDS = 5


LANGUAGE_CONFIG = {
    "python": {
        "extension": ".py",
        "command_candidates": ["python3", "python"],
    },
    "javascript": {
        "extension": ".js",
        "command_candidates": ["node"],
    },
}


def _truncate_text(text: str, max_bytes: int = MAX_OUTPUT_SIZE_BYTES) -> str:
    encoded = text.encode("utf-8", errors="replace")
    if len(encoded) <= max_bytes:
        return text

    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
    suffix = "\n... output truncated ..."
    return truncated + suffix


def _resolve_interpreter(command_candidates: list[str]) -> str | None:
    for candidate in command_candidates:
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def run_code(language: str, content: str) -> Dict[str, str | int]:
    language_normalized = (language or "").strip().lower()

    if language_normalized not in LANGUAGE_CONFIG:
        return {
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "exitCode": 1,
        }

    if not isinstance(content, str):
        return {
            "stdout": "",
            "stderr": "Invalid content: content must be a string",
            "exitCode": 1,
        }

    content_size = len(content.encode("utf-8", errors="replace"))
    if content_size > MAX_CODE_SIZE_BYTES:
        return {
            "stdout": "",
            "stderr": "Code size exceeds limit of 50KB",
            "exitCode": 1,
        }

    config = LANGUAGE_CONFIG[language_normalized]
    interpreter = _resolve_interpreter(config["command_candidates"])

    if not interpreter:
        missing_name = config["command_candidates"][0]
        return {
            "stdout": "",
            "stderr": f"Interpreter not found: {missing_name}",
            "exitCode": 1,
        }

    temp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=config["extension"],
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(content)
            temp_file.flush()
            temp_file_path = temp_file.name

        completed = subprocess.run(
            [interpreter, temp_file_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=RUN_TIMEOUT_SECONDS,
            shell=False,
        )

        stdout = _truncate_text(completed.stdout or "")
        stderr = _truncate_text(completed.stderr or "")

        return {
            "stdout": stdout,
            "stderr": stderr,
            "exitCode": completed.returncode,
        }

    except subprocess.TimeoutExpired as exc:
        stdout = _truncate_text(exc.stdout or "" if isinstance(exc.stdout, str) else "")
        stderr = _truncate_text(exc.stderr or "" if isinstance(exc.stderr, str) else "")

        timeout_message = "timeout exceeded"
        if stderr:
            stderr = f"{stderr}\n{timeout_message}"
        else:
            stderr = timeout_message

        return {
            "stdout": stdout,
            "stderr": _truncate_text(stderr),
            "exitCode": 124,
        }

    except Exception as exc:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(exc)}",
            "exitCode": 1,
        }

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass