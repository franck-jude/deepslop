import time
import importlib
from pathlib import Path
import yaml

class DeepSeekUI:
    def __init__(self, config_path: Path = Path("config/default.yaml"), pyautogui_module=None, pyperclip_module=None):
        # Évite l'import global pour que les tests puissent mocker
        self.pyautogui = pyautogui_module or importlib.import_module("pyautogui")
        self.pyperclip = pyperclip_module or importlib.import_module("pyperclip")

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
        self.pyautogui.click(self.text_x, self.text_y)
        time.sleep(0.2)
        self.pyautogui.hotkey("ctrl", "a")
        self.pyautogui.press("delete")
        self.pyperclip.copy(prompt)
        self.pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
        self.pyautogui.press("enter")
        return self._wait_for_new_clipboard()

    def _wait_for_new_clipboard(self) -> str:
        original = self.pyperclip.paste()
        elapsed = 0

        while elapsed < self.max_wait:
            self.pyautogui.click(self.copy_x, self.copy_y)
            time.sleep(0.1)
            current = self.pyperclip.paste()

            if current and current != original and len(current) > 50:
                return current

            time.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError(f"Pas de réponse détectée après {self.max_wait}s")