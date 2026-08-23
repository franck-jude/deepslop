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