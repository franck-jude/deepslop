.PHONY: test install clean

install:
	pip install -e .

test:
	pytest

coverage:
	pytest --cov=agent --cov-report=html

clean:
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +