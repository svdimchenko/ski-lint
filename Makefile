.PHONY: setup
setup:
	poetry install
	poetry run pre-commit install --overwrite --install-hooks

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: test tests
test tests:
	poetry run nox
