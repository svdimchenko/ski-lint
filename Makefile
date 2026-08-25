.PHONY: setup
setup:
	poetry install
	prek install

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: test tests
test tests:
	poetry run nox
