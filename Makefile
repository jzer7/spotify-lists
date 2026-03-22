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
help: ## Display help information for Makefile targets
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ----------------------------------------------------------
# Setup environment
# ----------------------------------------------------------

.PHONY: setup
setup: setup-python ## Set up the development environment
	@echo "Development environment setup complete."

.PHONY: rebuild-venv
rebuild-venv: ## Rebuild the Python virtual environment from scratch
	@echo "Rebuilding the Python virtual environment..."
	@uv venv -p $(PYTHON_VERSION) --clear
	$(MAKE) setup-python

.PHONY: setup-python
setup-python: ## Set up the development environment for Python
	@echo "Setting up the development environment for Python..."
	@uv lock --check-exists
	@uv sync --no-dev -p $(PYTHON_VERSION)
	@echo "Python environment setup complete."

# ----------------------------------------------------------
# Test
# ----------------------------------------------------------

.PHONY: test
test: ## Run tests

# ----------------------------------------------------------
# Linting
# ----------------------------------------------------------

.PHONY: lint
lint: lint-python lint-shell ## Lint all artifacts
	@echo "Completed linting all artifacts."

.PHONY: lint-python
lint-python: ## Lint all Python scripts
	@echo "Linting Python scripts..."
	@uv run ruff check scripts/

.PHONY: lint-shell
lint-shell: ## Lint all shell scripts
	@echo "Linting shell scripts..."
	@find . -type f -exec grep -q '^#!.*sh' {} \; -exec docker run --rm -it -v "$$(pwd):/mnt" $(SHELLCHECK) -x {} +

# ----------------------------------------------------------
# Clean Up
# ----------------------------------------------------------

.PHONY: clean
clean: ## Clean up generated artifacts
	rm -rf .coverage
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	find . -name __pycache__ -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
