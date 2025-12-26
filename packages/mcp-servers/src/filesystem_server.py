"""
Filesystem MCP Server
=====================

Git-aware file operations for code generation and brownfield analysis.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file."""
    path: Path
    exists: bool
    size: int = 0
    is_dir: bool = False
    git_status: Optional[str] = None  # M, A, D, ??, etc.


@dataclass
class GitInfo:
    """Git repository information."""
    is_repo: bool
    root: Optional[Path] = None
    branch: Optional[str] = None
    has_changes: bool = False
    remote: Optional[str] = None


def get_git_info(path: Path) -> GitInfo:
    """Get git information for a path."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path if path.is_dir() else path.parent,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return GitInfo(is_repo=False)

        root = Path(result.stdout.strip())

        # Get branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else None

        # Check for changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        has_changes = bool(status_result.stdout.strip())

        # Get remote
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        remote = remote_result.stdout.strip() if remote_result.returncode == 0 else None

        return GitInfo(
            is_repo=True,
            root=root,
            branch=branch,
            has_changes=has_changes,
            remote=remote,
        )
    except Exception:
        return GitInfo(is_repo=False)


def get_file_info(path: Path) -> FileInfo:
    """Get information about a file."""
    git_status = None

    if path.exists():
        git_info = get_git_info(path)
        if git_info.is_repo:
            # Get git status for this file
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain", str(path)],
                    cwd=git_info.root,
                    capture_output=True,
                    text=True,
                )
                if result.stdout.strip():
                    git_status = result.stdout.strip()[:2].strip()
            except Exception:
                pass

    return FileInfo(
        path=path,
        exists=path.exists(),
        size=path.stat().st_size if path.exists() and path.is_file() else 0,
        is_dir=path.is_dir() if path.exists() else False,
        git_status=git_status,
    )


def read_file(path: Path) -> tuple[bool, str]:
    """Read a file's contents."""
    try:
        return True, path.read_text()
    except Exception as e:
        return False, str(e)


def write_file(path: Path, content: str, create_dirs: bool = True) -> tuple[bool, str]:
    """Write content to a file."""
    try:
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return True, f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return False, str(e)


def list_files(
    path: Path,
    pattern: str = "*",
    recursive: bool = False,
    ignore_patterns: Optional[list[str]] = None,
) -> list[FileInfo]:
    """List files in a directory."""
    ignore_patterns = ignore_patterns or []

    def should_ignore(p: Path) -> bool:
        for pattern in ignore_patterns:
            if p.match(pattern):
                return True
        return False

    files = []
    glob_method = path.rglob if recursive else path.glob

    for file_path in glob_method(pattern):
        if not should_ignore(file_path):
            files.append(get_file_info(file_path))

    return files


def git_commit(path: Path, message: str, add_all: bool = True) -> tuple[bool, str]:
    """Create a git commit."""
    git_info = get_git_info(path)
    if not git_info.is_repo:
        return False, "Not a git repository"

    try:
        if add_all:
            subprocess.run(["git", "add", "-A"], cwd=git_info.root, check=True)

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=git_info.root,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)


def git_diff(path: Path, staged: bool = False) -> tuple[bool, str]:
    """Get git diff."""
    git_info = get_git_info(path)
    if not git_info.is_repo:
        return False, "Not a git repository"

    try:
        cmd = ["git", "diff"]
        if staged:
            cmd.append("--staged")

        result = subprocess.run(
            cmd,
            cwd=git_info.root,
            capture_output=True,
            text=True,
        )
        return True, result.stdout
    except Exception as e:
        return False, str(e)


# MCP Tool definitions
FILESYSTEM_TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"},
                "create_dirs": {"type": "boolean", "default": True},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_files",
        "description": "List files in a directory",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path"},
                "pattern": {"type": "string", "default": "*"},
                "recursive": {"type": "boolean", "default": False},
                "ignore_patterns": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["path"],
        },
    },
    {
        "name": "git_info",
        "description": "Get git repository information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path within the repo"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "git_commit",
        "description": "Create a git commit",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "message": {"type": "string"},
                "add_all": {"type": "boolean", "default": True},
            },
            "required": ["path", "message"],
        },
    },
    {
        "name": "git_diff",
        "description": "Get git diff",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "staged": {"type": "boolean", "default": False},
            },
            "required": ["path"],
        },
    },
]


def handle_read_file(params: dict) -> dict:
    """Handle read_file tool call."""
    path = Path(params["path"])
    success, content = read_file(path)
    return {"success": success, "content": content if success else None, "error": None if success else content}


def handle_write_file(params: dict) -> dict:
    """Handle write_file tool call."""
    path = Path(params["path"])
    success, message = write_file(path, params["content"], params.get("create_dirs", True))
    return {"success": success, "message": message}


def handle_list_files(params: dict) -> dict:
    """Handle list_files tool call."""
    path = Path(params["path"])
    files = list_files(
        path,
        params.get("pattern", "*"),
        params.get("recursive", False),
        params.get("ignore_patterns"),
    )
    return {
        "files": [
            {
                "path": str(f.path),
                "exists": f.exists,
                "size": f.size,
                "is_dir": f.is_dir,
                "git_status": f.git_status,
            }
            for f in files
        ]
    }


def handle_git_info(params: dict) -> dict:
    """Handle git_info tool call."""
    path = Path(params["path"])
    info = get_git_info(path)
    return {
        "is_repo": info.is_repo,
        "root": str(info.root) if info.root else None,
        "branch": info.branch,
        "has_changes": info.has_changes,
        "remote": info.remote,
    }


def handle_git_commit(params: dict) -> dict:
    """Handle git_commit tool call."""
    path = Path(params["path"])
    success, message = git_commit(path, params["message"], params.get("add_all", True))
    return {"success": success, "message": message}


def handle_git_diff(params: dict) -> dict:
    """Handle git_diff tool call."""
    path = Path(params["path"])
    success, diff = git_diff(path, params.get("staged", False))
    return {"success": success, "diff": diff if success else None, "error": None if success else diff}
