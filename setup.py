import pyautogui
import json
import time

print("Place la souris sur la zone de texte de DeepSeek et appuie sur ENTRÉE")
input()
text_x, text_y = pyautogui.position()
print(f"Zone de texte : ({text_x}, {text_y})")

print("Place la souris sur le bouton Copier et appuie sur ENTRÉE")
input()
copy_x, copy_y = pyautogui.position()
print(f"Bouton Copier : ({copy_x}, {copy_y})")

coords = {
    "ui": {
        "text_x": text_x,
        "text_y": text_y,
        "copy_x": copy_x,
        "copy_y": copy_y,
        "wait_time": 30
    }
}

with open("config/default.yaml", "w") as f:
    import yaml
    yaml.dump(coords, f)

print("✅ Config sauvegardée dans config/default.yaml")