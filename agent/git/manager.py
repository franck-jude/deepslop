import subprocess
import os
from pathlib import Path

class GitManager:
    def __init__(self, repo_path="."):
        self.repo_path = Path(repo_path)

    def _run(self, command, check=True):
        """Exécute une commande Git et retourne la sortie."""
        result = subprocess.run(
            command,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        if check and result.returncode != 0:
            raise RuntimeError(f"Git error: {result.stderr.strip()}")
        return result.stdout.strip()

    def init(self):
        """Initialise un dépôt Git."""
        if (self.repo_path / ".git").exists():
            return "Repository already initialized"
        self._run(["git", "init"])
        return "Initialized empty Git repository"

    def add(self, path="."):
        """Ajoute un fichier ou un dossier."""
        self._run(["git", "add", path])
        return f"Added {path}"

    def commit(self, message="Auto-commit"):
        """Commit les changements."""
        self._run(["git", "commit", "-m", message])
        return f"Committed: {message}"

    def status(self):
        """Retourne le statut Git."""
        output = self._run(["git", "status", "--short"], check=False)
        return output or "No changes"

    def diff(self):
        """Retourne les différences non commitées."""
        output = self._run(["git", "diff"], check=False)
        return output or "No differences"

    def branch(self):
        """Retourne la branche courante."""
        output = self._run(["git", "branch", "--show-current"], check=False)
        return output or "main"

    def log(self, n=5):
        """Retourne les derniers commits."""
        output = self._run(["git", "log", f"-{n}", "--oneline"], check=False)
        return output or "No commits yet"

    def is_repo(self):
        """Vérifie si le dossier est un dépôt Git."""
        return (self.repo_path / ".git").exists()