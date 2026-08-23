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

        # Nettoyage des balises [code] et <code>
        lines = response.splitlines()
        clean_lines = []
        in_code = False
        for line in lines:
            if "[code]" in line or "<code>" in line:
                in_code = True
                continue
            if "[/code]" in line or "</code>" in line:
                in_code = False
                continue
            if in_code:
                clean_lines.append(line)

        response = "\n".join(clean_lines)
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
            print("⚠️ Action Git inconnue : {action}") 

    else:
        raise ValueError("Type de step inconnu : {step_type}")


def execute_steps(steps: list, context: dict) -> None:
    for step in steps:
        execute_step(step, context)