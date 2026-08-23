import os

files = {
    "agent/io/parser.py": '''
import re
from typing import Dict, Optional

def extract_files(response: str, default_path: Optional[str] = None) -> Dict[str, str]:
    result = {}

    pattern = r"Create a file\s+([\w/]+\.py)\s*\n\[code\]\n(.*?)\n\[/code\]"
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
    for path, content in matches:
        result[path] = content.strip()

    if result:
        return result

    pattern = r"# Create a file\s+([\w/]+\.py)\s*\n# \[code\]\n(.*?)\n# \[/code\]"
    matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
    for path, content in matches:
        result[path] = content.strip()

    if result:
        return result

    if default_path and response.strip():
        clean = response.strip()
        for marker in ["[code]", "```python", "```"]:
            if clean.startswith(marker):
                clean = clean[len(marker):]
            if clean.endswith("```"):
                clean = clean[:-3]
        result[default_path] = clean.strip()

    return result

def parse_files(response: str, default_path: Optional[str] = None) -> Dict[str, str]:
    return extract_files(response, default_path)
''',

    "agent/io/filesystem.py": '''
from pathlib import Path
from datetime import datetime
import shutil

def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_file(path: Path, content: str) -> None:
    ensure_dir(path)
    path.write_text(content, encoding="utf-8")

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def backup_file(path: Path, backup_dir: Path = Path("backups")) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{path.stem}_{ts}{path.suffix}"
    shutil.copy2(path, backup_path)
    return backup_path

def restore_file(path: Path, backup_path: Path) -> None:
    shutil.copy2(backup_path, path)

def file_exists(path: Path) -> bool:
    return path.exists()

def delete_file(path: Path) -> None:
    if path.exists():
        path.unlink()
''',

    "agent/ui/browser.py": '''
import time
import pyautogui
import pyperclip
from pathlib import Path
import yaml

class DeepSeekUI:
    def __init__(self, config_path: Path = Path("config/default.yaml")):
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        coords = config["ui"]

        self.text_x = coords["text_x"]
        self.text_y = coords["text_y"]
        self.copy_x = coords["copy_x"]
        self.copy_y = coords["copy_y"]
        self.poll_interval = coords.get("poll_interval", 0.5)
        self.max_wait = coords.get("max_wait", 60)

    def ask(self, prompt: str) -> str:
        pyautogui.click(self.text_x, self.text_y)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("delete")

        pyperclip.copy(prompt)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)

        pyautogui.press("enter")
        time.sleep(1)

        pyautogui.click(self.text_x, self.text_y)
        time.sleep(0.2)
        pyautogui.scroll(-400)
        time.sleep(0.5)

        return self._wait_for_new_clipboard()

    def _wait_for_new_clipboard(self) -> str:
        original = pyperclip.paste()
        elapsed = 0
        last_content = original
        stable_count = 0

        while elapsed < self.max_wait:
            pyautogui.click(self.copy_x, self.copy_y)
            time.sleep(0.1)
            current = pyperclip.paste()

            if current and current != original and len(current) > 50:
                if len(current) > len(original) + 50:
                    return current
                if current == last_content:
                    stable_count += 1
                    if stable_count >= 3:
                        return current
                else:
                    stable_count = 0
                    last_content = current

            time.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(f"Pas de réponse détectée après {self.max_wait}s")
''',

    "agent/git/manager.py": '''
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
''',

    "agent/steps/engine.py": '''
from pathlib import Path
import subprocess
from agent.io.filesystem import write_file
from agent.ui.browser import DeepSeekUI

def execute_step(step: dict, context: dict) -> None:
    step_type = step.get("type")
    root = context.get("root", Path.cwd())

    if step_type == "write_file":
        filepath = root / step["path"]
        write_file(filepath, step["content"])

    elif step_type == "mkdir":
        dirpath = root / step["path"]
        dirpath.mkdir(parents=True, exist_ok=True)

    elif step_type == "command":
        subprocess.run(step["command"], shell=True, cwd=context.get("cwd", root))

    elif step_type == "ask":
        ui = DeepSeekUI()
        prompt = step.get("prompt", "What do you suggest?")
        response = ui.ask(prompt)
        context["last_response"] = response
        print("📥 Réponse nettoyée reçue")

    elif step_type == "parse":
        response = context.get("last_response", "")
        if not response:
            print("⚠️ Aucune réponse à parser")
            return

        default_path = step.get("path", None)
        from agent.io.parser import extract_files
        files = extract_files(response, default_path=default_path)

        if not files:
            print("⚠️ Aucun fichier trouvé")
            return

        for filepath, content in files.items():
            full_path = Path(filepath)
            write_file(full_path, content)
            print(f"✅ Fichier écrit : {full_path}")

    elif step_type == "git":
        from agent.git.manager import GitManager
        git = GitManager(str(root))
        action = step.get("action")

        if action == "init":
            print(git.init())
        elif action == "add":
            path = step.get("path", ".")
            print(git.add(path))
        elif action == "commit":
            msg = step.get("message", "Auto-commit")
            print(git.commit(msg))
        elif action == "status":
            print(git.status())
        elif action == "diff":
            print(git.diff())
        else:
            print(f"⚠️ Action Git inconnue : {action}")

    else:
        raise ValueError(f"Type de step inconnu : {step_type}")

def execute_steps(steps: list, context: dict) -> None:
    for step in steps:
        execute_step(step, context)
'''
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ {path} restauré")