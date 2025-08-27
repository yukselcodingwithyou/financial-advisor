.PHONY: help install install-dev test lint format run docker-up docker-down ingest rag clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test: ## Run tests
	pytest -v tests/

test-cov: ## Run tests with coverage
	pytest --cov=src --cov=advanced --cov-report=html --cov-report=term tests/

lint: ## Run linting
	ruff check .
	ruff format --check .

format: ## Format code
	ruff format .
	ruff check --fix .

run: ## Run FastAPI server
	uvicorn advanced.api_fastapi.main:app --reload --host 0.0.0.0 --port 8000

streamlit: ## Run Streamlit demo
	streamlit run app_streamlit.py

docker-build: ## Build Docker image
	docker build -t financial-advisor .

docker-up: ## Start all services with docker-compose
	docker compose up --build -d

docker-down: ## Stop all services
	docker compose down

docker-logs: ## View logs from all services
	docker compose logs -f

ingest: ## Ingest sample data for RAG
	python src/rag/cli_ingest_pgvector.py --sample

rag: ## Test RAG functionality
	python -c "from src.rag.rag_minimal import test_rag; test_rag()"

dbt-run: ## Run dbt models
	cd advanced/dbt_project && dbt run

dbt-test: ## Run dbt tests
	cd advanced/dbt_project && dbt test

feast-apply: ## Apply Feast feature definitions
	cd advanced/feast_repo && feast apply

generate-diagrams: ## Generate architecture diagrams
	python scripts/generate_architecture.py
	python scripts/generate_sequence.py
	python scripts/generate_dbt_featurestore_flow.py

benchmark: ## Run optimization benchmarks
	python scripts/bench_compare_mv_cvar.py

report: ## Generate sample report
	python scripts/render_report.py

clean: ## Clean up temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "htmlcov" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".ruff_cache" -exec rm -rf {} +

bootstrap: ## Initialize git repository with staged commits
	bash scripts/bootstrap_with_commits.sh

dev-setup: install-dev generate-diagrams ## Complete development setup
	@echo "Development environment ready!"