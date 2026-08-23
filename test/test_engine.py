import pytest
from unittest.mock import patch, MagicMock
from agent.steps.engine import execute_step


def test_execute_ask():
    step = {"type": "ask", "prompt": "Hello"}
    context = {}

    with patch("agent.steps.engine.DeepSeekUI") as MockUI:
        mock_instance = MockUI.return_value
        mock_instance.ask.return_value = "[code]\nMocked response\n[/code]"

        execute_step(step, context)

        mock_instance.ask.assert_called_once_with("Hello")
        # La réponse est nettoyée : on attend "Mocked response"
        assert context.get("last_response") == "Mocked response"


def test_execute_parse_without_response():
    step = {"type": "parse"}
    context = {}
    execute_step(step, context)
    assert "last_response" not in context