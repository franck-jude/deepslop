import sys
from unittest.mock import MagicMock

# Mock pyautogui pour tous les tests
sys.modules['pyautogui'] = MagicMock()