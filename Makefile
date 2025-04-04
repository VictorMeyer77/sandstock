.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[test]

.PHONY: fmt
fmt:              ## Format code using black & isort.
	$(ENV_PREFIX)isort sandstock/
	$(ENV_PREFIX)isort tests/
	$(ENV_PREFIX)black -l 120 sandstock/
	$(ENV_PREFIX)black -l 120 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	$(ENV_PREFIX)flake8 --max-line-length 120 sandstock/
	$(ENV_PREFIX)flake8 --max-line-length 120 tests/
	$(ENV_PREFIX)black -l 120 --check sandstock/
	$(ENV_PREFIX)black -l 120 --check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports sandstock/
	$(ENV_PREFIX)mypy --ignore-missing-imports tests/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	@docker run -d --name azure-sql-edge -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Te54?ko1" -e "MSSQL_PID=Developer" -p 57000:1433 --restart always  mcr.microsoft.com/azure-sql-edge:latest
	@sleep 5
	$(ENV_PREFIX)TEST=true pytest -v --cov-config .coveragerc --cov=sandstock -l --tb=short --maxfail=1 -p no:logging tests/
	@docker stop azure-sql-edge
	@docker rm azure-sql-edge
	@PYTEST_EXIT_CODE=$$?
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html
	@exit $$PYTEST_EXIT_CODE

.PHONY: clean
clean:            ## Clean unused files.
	@rm -rf __pycache__
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build
	@rm -rf instance
	@rm -rf .coverage
	@rm -rf coverage.xml

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@echo "creating virtualenv ..."
	@rm -rf .venv
	@python3 -m venv .venv
	@./.venv/bin/pip install -U pip
	@./.venv/bin/pip install -e .[test]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	@$(ENV_PREFIX)mkdocs serve