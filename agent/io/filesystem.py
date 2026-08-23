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
    