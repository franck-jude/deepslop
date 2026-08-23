import re
from typing import Dict, Optional


class FileParser:
    @staticmethod
    def extract_files(
        response: str,
        default_path: Optional[str] = None,
        fallback_name: str = "modules/fallback.py"
    ) -> Dict[str, str]:
        result = {}

        # Format 1 : Create a file ... [code] ... [/code]
        pattern = r"Create a file\s+([\w/]+\.py)\s*\n\[code\]\n(.*?)\n\[/code\]"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        for path, content in matches:
            result[path] = content.strip()
        if result:
            return result

        # Format 2 : # Create a file ... # [code] ... # [/code]
        pattern = r"# Create a file\s+([\w/]+\.py)\s*\n# \[code\]\n(.*?)\n# \[/code\]"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        for path, content in matches:
            result[path] = content.strip()
        if result:
            return result

        # Format 3 : backticks + #
        pattern = r"```python\s*\n# Create a file\s+([\w/]+\.py)\s*\n# \[code\]\n(.*?)\n# \[/code\]\s*\n```"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        for path, content in matches:
            result[path] = content.strip()
        if result:
            return result

        # Format 4 : backticks seuls
        pattern = r"```python\s*\n(.*?)\n```"
        matches = re.findall(pattern, response, re.DOTALL)
        for idx, content in enumerate(matches):
            result[f"{fallback_name}_{idx}.py"] = content.strip()
        if result:
            return result

        # Format 5 : fallback ultime (on écrit tout dans default_path)
        if default_path and response.strip():
            clean = response.strip()
            for marker in ["[code]", "```python", "```"]:
                if clean.startswith(marker):
                    clean = clean[len(marker):]
                if clean.endswith("```"):
                    clean = clean[:-3]
            result[default_path] = clean.strip()
            return result

        # Format 6 : fallback générique
        if response.strip():
            clean = response.strip()
            for marker in ["[code]", "```python", "```"]:
                if clean.startswith(marker):
                    clean = clean[len(marker):]
                if clean.endswith("```"):
                    clean = clean[:-3]
            result[fallback_name] = clean.strip()
            return result

        return result

    @staticmethod
    def parse_files(response: str, default_path: Optional[str] = None) -> Dict[str, str]:
        return FileParser.extract_files(response, default_path)


# Aliases pour compatibilité
def extract_files(response: str, default_path: Optional[str] = None) -> Dict[str, str]:
    return FileParser.extract_files(response, default_path)

def parse_files(response: str, default_path: Optional[str] = None) -> Dict[str, str]:
    return FileParser.parse_files(response, default_path)