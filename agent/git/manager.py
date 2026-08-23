import subprocess
from pathlib import Path

class GitManager:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)

    def _run(self, command):
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()

    def init(self):
        return self._run(["git", "init"])

    def add(self, path="."):
        return self._run(["git", "add", path])

    def commit(self, message="Auto-commit"):
        return self._run(["git", "commit", "-m", message])

    def status(self):
        result = self._run(["git", "status", "--short"])
        return result or "No changes"

    def diff(self):
        result = self._run(["git", "diff"])
        return result or "No differences"
