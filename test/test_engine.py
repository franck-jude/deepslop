import pytest
from unittest.mock import MagicMock, patch
from agent.steps.engine import execute_step


def test_execute_ask():
    step = {"type": "ask", "prompt": "Hello"}
    context = {}

    with patch("agent.steps.engine.DeepSeekUI") as MockUI:
        mock_instance = MockUI.return_value
        # La réponse doit contenir [code] pour être nettoyée
        mock_instance.ask.return_value = "[code]\nMocked response\n[/code]"

        execute_step(step, context)

        mock_instance.ask.assert_called_once_with("Hello")
        assert context.get("last_response") == "Mocked response"


def test_execute_parse_without_response():
    step = {"type": "parse"}
    context = {}
    execute_step(step, context)
    assert "last_response" not in context