.PHONY: setup install test clean help activate

# Variables
PYTHON_VERSION = 3.12
VENV = .venv
UV = uv

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Create a virtual environment with uv
	$(UV) venv --python $(PYTHON_VERSION)

install: ## Install dependencies from requierements.txt
	$(UV) pip install -r requierements.txt

activate: ## Instructions to activate the environment
	@echo "Run the following command to activate your environment:"
	@echo "source $(VENV)/bin/activate"

test: ## Run tests using uv run (no activation needed)
	$(UV) run pytest utils/

clean: ## Remove the virtual environment
	rm -rf $(VENV)
