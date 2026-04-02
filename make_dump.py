from pathlib import Path

OUTPUT_FILE = "project_dump.txt"

EXCLUDED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    ".pytest_cache",
}

EXCLUDED_FILES = {
    OUTPUT_FILE,
}

TEXT_FILE_EXTENSIONS = {
    ".py",
    ".txt",
    ".md",
    ".json",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".scss",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".env",
    ".gitignore",
}


def is_text_file(path: Path) -> bool:
    if path.name in EXCLUDED_FILES:
        return False

    if path.suffix.lower() in TEXT_FILE_EXTENSIONS:
        return True

    if path.name in {"Dockerfile", "requirements.txt", ".gitignore"}:
        return True

    return False


def should_skip_dir(path: Path) -> bool:
    return path.name in EXCLUDED_DIRS


def build_tree(root: Path) -> list[str]:
    lines = []

    def walk(current: Path, prefix: str = ""):
        entries = sorted(
            [p for p in current.iterdir() if p.name not in EXCLUDED_FILES],
            key=lambda p: (p.is_file(), p.name.lower())
        )

        entries = [p for p in entries if not (p.is_dir() and should_skip_dir(p))]

        for index, entry in enumerate(entries):
            connector = "└── " if index == len(entries) - 1 else "├── "
            lines.append(f"{prefix}{connector}{entry.name}")

            if entry.is_dir():
                extension = "    " if index == len(entries) - 1 else "│   "
                walk(entry, prefix + extension)

    lines.append(root.name)
    walk(root)
    return lines


def dump_files(root: Path) -> list[str]:
    lines = []

    for path in sorted(root.rglob("*")):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.is_dir():
            continue
        if path.name in EXCLUDED_FILES:
            continue
        if not is_text_file(path):
            continue

        relative_path = path.relative_to(root)

        lines.append("\n" + "=" * 100)
        lines.append(f"FILE: {relative_path}")
        lines.append("=" * 100)

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except Exception as exc:
                content = f"[ERROR READING FILE: {exc}]"
        except Exception as exc:
            content = f"[ERROR READING FILE: {exc}]"

        lines.append(content)

    return lines


def main():
    root = Path.cwd()
    output_path = root / OUTPUT_FILE

    result = []

    result.append("PROJECT TREE")
    result.append("=" * 100)
    result.extend(build_tree(root))

    result.append("\n\nPROJECT FILE CONTENTS")
    result.append("=" * 100)
    result.extend(dump_files(root))

    output_path.write_text("\n".join(result), encoding="utf-8")
    print(f"Done. Project dump saved to: {output_path}")


if __name__ == "__main__":
    main()