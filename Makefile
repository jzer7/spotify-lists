SHELLCHECK      := koalaman/shellcheck:stable
PYTHON_VERSION  := 3.12

# Get the current Git hash
GIT_HASH := $(shell git rev-parse --short HEAD)
ifneq ($(shell git status --porcelain),)
	# There are untracked changes
	GIT_HASH := $(GIT_HASH)+
endif

# Capture the current build date in RFC3339 format
BUILD_DATE := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help
help: ## ❓ Display help information for Makefile targets
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ----------------------------------------------------------
# Setup environment
# ----------------------------------------------------------

.PHONY: setup
setup: setup-simple ## ⚙️ Set up the development environment
	@echo "Development environment setup complete."

.PHONY: rebuild-venv
rebuild-venv: ## 🔄 Rebuild the Python virtual environment from scratch
	@echo "Rebuilding the Python virtual environment..."
	@uv venv -p $(PYTHON_VERSION) --clear
	$(MAKE) setup-simple

.PHONY: setup-simple
setup-simple: ## ⚙️ Set up a Python environment without development dependencies
	@echo "Setting up a simple Python environment..."
	@uv lock --check-exists
	@uv sync --no-dev -p $(PYTHON_VERSION)
	@echo "Python environment setup complete."

.PHONY: setup-ci
setup-ci: ## ⚙️ Set up the CI environment
	@echo "Setting up the CI environment..."
	@uv lock --check-exists
	@uv sync --dev -p $(PYTHON_VERSION)
	@echo "CI environment setup complete."

# ----------------------------------------------------------
# Checks
# ----------------------------------------------------------

.PHONY: check
check: ruff mypy test-unit ## 🔍 Run quick checks (lint, type checking, and unit tests)

.PHONY: check-all
check-all: static test ## 🔍 Run all checks (static analysis and tests)

# ----------------------------------------------------------
# Static Analysis
# ----------------------------------------------------------

.PHONY: static
static: ruff mypy ## 🔍 Run all static analysis checks

# ----------------------------------------------------------
# Linting
# ----------------------------------------------------------

.PHONY: lint lint-python lint-shell
lint: lint-python ## 🧹 Lint artifacts
	@echo "Completed linting all artifacts."

lint-python: ruff ## 🧹 Lint all Python scripts with ruff
lint-shell: shellcheck ## 🧹 Lint all shell scripts with shellcheck

# ----------------------------------------------------------
# Static analysis tools
# ----------------------------------------------------------


.PHONY: mypy
mypy: ## 🧩 Type checking with mypy
	@echo "Checking types in Python scripts with mypy..."
	@uv run mypy src/
	@echo "Checking types in Python tests with mypy..."
	@uv run mypy tests/

.PHONY: ruff
ruff: ## 🧹 Lint all Python scripts with ruff
	@echo "Linting Python scripts with ruff..."
	@uv run ruff check src/
	@echo "Linting Python tests with ruff..."
	@uv run ruff check tests/

.PHONY: shellcheck
shellcheck:  ## 🧹 Lint all shell scripts with shellcheck
	@echo "Linting shell scripts with shellcheck..."
	@find . -type f -not -path "./.git/*" -exec grep -q '^#!.*sh' {} \; -exec docker run --rm -it -v "$$(pwd):/mnt" $(SHELLCHECK) -x {} +

# ----------------------------------------------------------
# Test
# ----------------------------------------------------------

.PHONY: test
test: test-unit test-e2e ## 🧪 Run tests

.PHONY: test-unit
test-unit: ## 🧪 Run unit tests
	@echo "Running unit tests..."
	@uv run pytest -v --cov=src --cov-report=xml

.PHONY: test-e2e
test-e2e: ## 🧪 Run end-to-end tests
	@echo "Running end-to-end tests..."
	@echo "Fetching well known playlist..."
	rm -f "playlists/Greatest Film Themes of All Time.yaml"
	mkdir -p playlists
	uv run listify download --id "6LFObuU0EvpaQLj1iueTHO"
	test -f "playlists/playlist_6LFObuU0EvpaQLj1iueTHO.yaml"
	yq .owner_id "playlists/playlist_6LFObuU0EvpaQLj1iueTHO.yaml" | grep "bbcmusicmagazine" || (echo "Owner ID does not match expected value" && exit 1)

# ----------------------------------------------------------
# Build
# ----------------------------------------------------------

.PHONY: build
build: ## 🚜 Build package
	@uv build

# ----------------------------------------------------------
# Clean Up
# ----------------------------------------------------------

.PHONY: clean
clean: ## 🧹 Clean up generated artifacts
	rm -rf .coverage
	rm -rf dist/
	find . -name __pycache__ -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +

clean-full: clean ## 🧹 Clean common and expensive artifacts
	rm -rf .ruff_cache
	rm -rf .mypy_cache
