.PHONY: help install dev test lint format clean run run-cli run-check docker-build docker-up docker-down docs

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Anna AI - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install transformers==4.38.2

install-dev: install ## Install dev dependencies
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	pip install -e ".[dev]"
	pre-commit install

dev: ## Alias for install-dev
	$(MAKE) install-dev

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v

test-fast: ## Run tests without coverage
	@echo "$(BLUE)Running fast tests...$(NC)"
	pytest -v --no-cov

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest -v --cov=BASE --cov-report=html
	@echo "$(GREEN)Coverage report: htmlcov/index.html$(NC)"

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 BASE --max-line-length=100 --ignore=E203,W503
	mypy BASE --ignore-missing-imports

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black BASE --line-length=100
	isort BASE --profile=black

format-check: ## Check code formatting without changes
	@echo "$(BLUE)Checking code format...$(NC)"
	black --check BASE --line-length=100
	isort --check-only BASE --profile=black

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/ htmlcov/ .coverage
	@echo "$(GREEN)Clean complete$(NC)"

run: ## Run Anna AI with GUI
	@echo "$(BLUE)Starting Anna AI with GUI...$(NC)"
	python main.py

run-cli: ## Run Anna AI in CLI mode
	@echo "$(BLUE)Starting Anna AI in CLI mode...$(NC)"
	python main.py --no-gui

run-check: ## Run system health checks
	@echo "$(BLUE)Running system health checks...$(NC)"
	python main.py --check

run-verbose: ## Run with verbose logging
	@echo "$(BLUE)Starting Anna AI with verbose logging...$(NC)"
	python main.py -v

run-api: ## Run API server
	@echo "$(BLUE)Starting Anna AI API server...$(NC)"
	python api_server.py

run-api-port: ## Run API server on custom port (use PORT=8000 make run-api-port)
	@echo "$(BLUE)Starting Anna AI API server on port $(PORT)...$(NC)"
	python api_server.py --port $(PORT)

run-api-debug: ## Run API server in debug mode
	@echo "$(BLUE)Starting Anna AI API server in debug mode...$(NC)"
	python api_server.py --debug

validate-config: ## Validate configuration
	@echo "$(BLUE)Validating configuration...$(NC)"
	python -c "from BASE.config_validator import ConfigValidator; v = ConfigValidator(); print(v.generate_report())"

generate-docs: ## Generate API documentation
	@echo "$(BLUE)Generating API documentation...$(NC)"
	curl -s http://localhost:5000/ | grep -A 1000 'Anna AI' > API_DOCS.html

monitor-performance: ## Run performance monitor
	@echo "$(BLUE)Starting performance monitor...$(NC)"
	python -m BASE.performance_monitor

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t anna-ai:latest .
	@echo "$(GREEN)Docker image built$(NC)"

docker-up: ## Start Docker containers with compose
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Containers started$(NC)"

docker-logs: ## View Docker container logs
	@echo "$(BLUE)Docker logs (Ctrl+C to exit)...$(NC)"
	docker compose logs -f

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker compose down
	@echo "$(GREEN)Containers stopped$(NC)"

docker-clean: ## Remove Docker images and volumes
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker compose down -v
	@echo "$(GREEN)Docker resources cleaned$(NC)"

docker-shell: ## Open shell in running container
	@echo "$(BLUE)Opening container shell...$(NC)"
	docker compose exec anna-ai /bin/bash

docker-stats: ## Show Docker resource usage
	@echo "$(BLUE)Docker resource usage...$(NC)"
	docker stats --no-stream

docker-phase3: ## Start Docker with Phase 3 (PostgreSQL + Redis)
	@echo "$(BLUE)Starting Docker with Phase 3 services...$(NC)"
	docker compose --profile phase3 up -d
	@echo "$(GREEN)Phase 3 containers started$(NC)"

migrate-up: ## Run database migrations (requires DATABASE_URL)
	@echo "$(BLUE)Running database migrations...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)Migrations complete$(NC)"

migrate-down: ## Rollback last migration
	@echo "$(BLUE)Rolling back migration...$(NC)"
	alembic downgrade -1

migrate-create: ## Create new migration (use: make migrate-create MSG="description")
	@echo "$(BLUE)Creating migration...$(NC)"
	alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)Migration created$(NC)"

docs: ## Generate project documentation
	@echo "$(BLUE)Documentation files:$(NC)"
	@echo "  - README.md (main documentation)"
	@echo "  - SETUP.md (installation guide)"
	@echo "  - DEVELOPMENT.md (development guide)"
	@echo ""

setup-hooks: ## Setup pre-commit hooks
	@echo "$(BLUE)Setting up pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed$(NC)"

run-hooks: ## Run pre-commit on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

.DEFAULT_GOAL := help
