export WORKDIR = $(shell pwd)

project=services
cdk_src = cdk
service_src = services
tests_src = tests

e2e_tests = $(tests_src)/e2e
int_tests = $(test_src)/integration
all_src = $(cdk_src) $(service_src) $(tests_src)

.PHONY: target
target:
	@$(MAKE) pr

.PHONY: dev
dev:
	pip install --upgrade pip pre-commit poetry
	poetry install
	pre-commit install

.PHONY: test
test:
	poetry run pytest --ignore $(e2e_tests) --ignore $(int_tests) --cov=$(project) --cov-report=xml --cov-report term

.PHONY: format
format:
	poetry run isort $(all_src)
	poetry run black $(all_src)

.PHONY: lint
lint: format
	poetry run flake8 $(all_src)

.PHONY: pre-commit
pre-commit:
	pre-commit run --show-diff-on-failure

.PHONY: pr
pr: lint mypy pre-commit test

.PHONY: mypy
mypy:
	poetry run mypy --pretty $(service_src) $(cdk_src)

.PHONY: synth
synth: deps
	poetry run cdk synth

.PHONY: deploy
deploy: deps
	poetry run cdk deploy

.PHONY: deploy/diff
deploy/diff: deps
	poetry run cdk diff

.PHONY: deploy/remove
deploy/remove:
	poetry run cdk destroy

.PHONY: deploy/destroy
deploy/destroy:
	poetry run cdk destroy

.PHONY: deps
deps:
	scripts/make-deps.sh

.PHONY: clean
clean:
	rm -rf cdk.out .vscode .pytest_cache .coverage coverage.xml .mypy_cache
	find services -type f -name "requirements.txt" -delete
	find services cdk tests -type d -name "__pycache__" -exec rm -rf {} \;
	poetry env remove --all
