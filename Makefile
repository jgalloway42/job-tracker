.PHONY: install format lint test check run seed dedup clean

install:
	pip install -r requirements.txt -r requirements-dev.txt

format:
	black app/ pages/ tests/ scripts/ Home.py

lint:
	pylint app/ pages/ tests/ scripts/ Home.py --fail-under=10.0

test:
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-fail-under=100

check: format lint test

run:
	streamlit run Home.py

seed:
	python scripts/seed_demo.py

dedup:
	python -c "from app.database import resolve_duplicates; from app.config import DB_PATH; resolve_duplicates(DB_PATH)"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".coverage" -delete
