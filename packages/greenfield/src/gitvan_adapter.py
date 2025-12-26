"""
gitvan Adapter
==============

Integration with Sean Chatman's gitvan (v3.1.0)
https://github.com/seanchatman/gitvan

gitvan provides git-native workflow automation:
- Structured commit patterns
- Branch management
- Artifact versioning
- Workflow hooks
"""

import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Any


@dataclass
class GitvanConfig:
    """Configuration for gitvan."""
    gitvan_path: Path = field(default_factory=lambda: Path("../gitvan"))
    auto_commit: bool = True
    commit_prefix: str = "blackice"
    branch_prefix: str = "gen"


@dataclass
class GitvanResult:
    """Result of a gitvan operation."""
    success: bool
    message: str = ""
    commit_sha: Optional[str] = None
    branch: Optional[str] = None


class GitvanAdapter:
    """
    Adapter for Sean Chatman's gitvan git workflow automation.

    gitvan provides:
    - Structured git workflows
    - Automatic branching strategies
    - Commit message conventions
    - Pre/post hooks for validation
    """

    def __init__(self, config: Optional[GitvanConfig] = None):
        self.config = config or GitvanConfig()
        self._verified = False

    def verify_installation(self) -> tuple[bool, str]:
        """Verify gitvan is installed."""
        gitvan_path = self.config.gitvan_path

        if not gitvan_path.exists():
            return False, f"gitvan not found at {gitvan_path}. Clone from: https://github.com/seanchatman/gitvan"

        package_json = gitvan_path / "package.json"
        if not package_json.exists():
            return False, f"gitvan package.json not found."

        self._verified = True
        return True, "gitvan ready"

    def create_generation_branch(
        self,
        spec_name: str,
        from_branch: str = "main",
        repo_path: Path = Path("."),
    ) -> GitvanResult:
        """
        Create a branch for code generation.

        Follows gitvan naming conventions.
        """
        branch_name = f"{self.config.branch_prefix}/{spec_name}"

        try:
            # Create branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name, from_branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return GitvanResult(success=False, message=result.stderr)

            return GitvanResult(
                success=True,
                message=f"Created branch {branch_name}",
                branch=branch_name,
            )
        except Exception as e:
            return GitvanResult(success=False, message=str(e))

    def commit_artifact(
        self,
        artifact,
        repo_path: Path = Path("."),
        message: Optional[str] = None,
    ) -> GitvanResult:
        """
        Commit a generated artifact using gitvan conventions.

        Commit message format:
        [blackice] <type>(<scope>): <description>

        Types: gen, fix, refactor, test
        """
        # Write artifact files
        for file_path, content in artifact.files.items():
            full_path = repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        # Stage files
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            capture_output=True,
        )

        # Build commit message
        if message is None:
            message = f"[{self.config.commit_prefix}] gen({artifact.spec.name}): Generate {artifact.name} v{artifact.version}"

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return GitvanResult(success=False, message=result.stderr)

        # Get commit SHA
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

        return GitvanResult(
            success=True,
            message=f"Committed artifact",
            commit_sha=sha,
        )

    def commit_with_fmea(
        self,
        artifact,
        fmea_report: dict,
        repo_path: Path = Path("."),
    ) -> GitvanResult:
        """
        Commit artifact with FMEA report in commit message.

        This follows Sean's pattern of including failure mode
        analysis in the git history.
        """
        # Write artifact
        for file_path, content in artifact.files.items():
            full_path = repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        # Write FMEA report
        fmea_path = repo_path / ".blackice" / "fmea" / f"{artifact.name}.json"
        fmea_path.parent.mkdir(parents=True, exist_ok=True)
        fmea_path.write_text(json.dumps(fmea_report, indent=2))

        # Stage
        subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True)

        # Build FMEA-aware commit message
        risk_level = fmea_report.get("risk_level", "unknown")
        failure_modes = len(fmea_report.get("failure_modes", []))

        message = f"""[{self.config.commit_prefix}] gen({artifact.spec.name}): Generate {artifact.name}

FMEA Analysis:
- Risk Level: {risk_level}
- Failure Modes Analyzed: {failure_modes}
- Poka-Yoke Applied: {fmea_report.get('poka_yoke_count', 0)}

Generated by BLACKICE with ggen ontology pipeline.
"""

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return GitvanResult(success=False, message=result.stderr)

        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        return GitvanResult(
            success=True,
            message="Committed with FMEA report",
            commit_sha=sha_result.stdout.strip(),
        )

    def tag_release(
        self,
        version: str,
        repo_path: Path = Path("."),
        message: Optional[str] = None,
    ) -> GitvanResult:
        """Tag a release version."""
        tag_name = f"v{version}"
        message = message or f"Release {version}"

        result = subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", message],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return GitvanResult(success=False, message=result.stderr)

        return GitvanResult(
            success=True,
            message=f"Tagged {tag_name}",
        )
