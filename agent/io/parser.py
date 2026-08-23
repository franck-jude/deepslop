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