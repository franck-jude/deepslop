from pathlib import Path
import subprocess
import logging
import re
from agent.io.filesystem import write_file
from agent.ui.browser import DeepSeekUI
from agent.io.parser import extract_files
from agent.git.manager import GitManager

def clean_code(content: str) -> str:
    """Nettoie le code pour éviter les erreurs d'indentation."""
    lines = content.splitlines()
    cleaned = []
    in_code = False
    for line in lines:
        stripped = line.strip()
        if not stripped and not in_code:
            continue
        if stripped.startswith("```") or stripped.startswith("[code]"):
            in_code = not in_code
            continue
        if in_code:
            # Supprimer les # en début de ligne
            if stripped.startswith("#"):
                stripped = stripped[1:].strip()
            cleaned.append(stripped)
    return "\n".join(cleaned)

def execute_step(step: dict, context: dict) -> None:
    step_type = step.get("type")
    root = context.get("root", Path.cwd())

    if step_type == "write_file":
        filepath = root / step["path"]
        content = step.get("content", "")
        write_file(filepath, content)

    elif step_type == "mkdir":
        dirpath = root / step["path"]
        dirpath.mkdir(parents=True, exist_ok=True)

    elif step_type == "command":
        result = subprocess.run(step["command"], shell=True, cwd=context.get("cwd", root))
        if result.returncode != 0:
            print(f"⚠️ Commande échouée: {step['command']}")

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
        files = extract_files(response, default_path=default_path)
        if not files:
            print("⚠️ Aucun fichier trouvé")
            return
        for filepath, content in files.items():
            # 🔥 Nettoyer le code avant d'écrire
            clean = clean_code(content)
            full_path = Path(filepath)
            write_file(full_path, clean)
            print(f"✅ Fichier écrit : {full_path}")

    elif step_type == "git":
        git = GitManager(str(root))
        action = step.get("action")
        if action == "init":
            print(git.init())
        elif action == "add":
            path = step.get("path", ".")
            try:
                print(git.add(path))
            except FileNotFoundError as e:
                print(f"⚠️ {e}")
        elif action == "commit":
            msg = step.get("message", "Auto-commit")
            print(git.commit(msg))
        elif action == "status":
            print(git.status())
        elif action == "diff":
            print(git.diff())
        elif action == "log":
            print(git.log())
        else:
            print(f"⚠️ Action Git inconnue : {action}")

    else:
        raise ValueError(f"Type de step inconnu : {step_type}")

def execute_steps(steps: list, context: dict) -> None:
    for step in steps:
        execute_step(step, context)