import sys
import yaml
from pathlib import Path
from agent.steps.engine import execute_steps

def load_steps(path: Path) -> list:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("steps", [])

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py steps.yaml")
        return

    steps_file = Path(sys.argv[1])
    context = {"root": Path.cwd()}
    steps = load_steps(steps_file)
    execute_steps(steps, context)
    print("Steps executed successfully")

if __name__ == "__main__":
    main()