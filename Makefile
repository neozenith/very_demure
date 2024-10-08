# Ensure the .make folder exists when starting make
# We need this for build targets that have multiple or no file output.
# We 'touch' files in here to mark the last time the specific job completed.
_ := $(shell mkdir -p .make)
SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

# Derive the app name from the git remote repo name and not trust what the local folder name is.
# https://stackoverflow.com/a/42543006/622276
GIT_REMOTE_URL=$(shell git config --get remote.origin.url)
APP_NAME=$(shell basename -s .git ${GIT_REMOTE_URL})
APP_NAME_KEBAB=$(APP_NAME)
APP_NAME_SNAKE=$(subst -,_,$(APP_NAME))

AWS_ACCOUNT_ID=
AWS_PROFILE=
include .env

AWS_ECR_REGION=ap-southeast-2
ECR_REGISTRY=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com
ECR_REPOSITORY=$(ECR_REGISTRY)/$(APP_NAME_KEBAB)
DOCKER_PYTHON_BASE=3.12-slim


all: init lock dev fix docs typecheck test

# Named targets are ".PHONY" and get built always. Do not depend on them in the Makefile build chain.
.PHONY: all init lock prod dev clean docker-build docker-run docker-push docker-login debug_env

debug_env:
	@echo $(DOT_ENV_FILE)
	@echo $(AWS_PROFILE)
	@echo $(ECR_REGISTRY)

# ==================== SETUP ====================



# Ensure the virtualenvironment is created
init: .venv/bin/python3 requirements%.txt
# Ensure the virtual environment has the correct basic tooling before we get to the pyproject.toml
.venv/bin/python3:
	[ ! -d ".venv" ] && python3 -m venv .venv || echo ".venv already setup"
	.venv/bin/python3 -m pip install -qq --upgrade pip uv build wheel pre-commit
	.venv/bin/pre-commit install

# Ensure the lock files get generated based on changes to pyproject.toml
lock: requirements%.txt uv.lock
uv.lock: pyproject.toml .venv/bin/python3
	.venv/bin/python3 -m uv lock
requirements%.txt: pyproject.toml .venv/bin/python3
# Prod only deps
	.venv/bin/python3 -m uv pip compile --no-cache --refresh --generate-hashes --upgrade  -o requirements-macos.txt pyproject.toml
# Prod conatiner only deps
	.venv/bin/python3 -m uv pip compile \
	--python-platform linux \
	--no-cache --refresh --generate-hashes --upgrade  \
	-o requirements-container.txt pyproject.toml

# Dev dependencies
	.venv/bin/python3 -m uv pip compile --no-cache --refresh  --extra dev --upgrade  -o requirements-dev-macos.txt pyproject.toml

# Install the necessary dependencies depending if it is prod or dev build
# The .make/*-deps-installed is a sentinel file we 'touch' to mark the job complete with '@touch $@'
prod: .make/prod-deps-installed
.make/prod-deps-installed: requirements-macos.txt
	.venv/bin/python3 -m uv pip install \
    	--require-hashes --no-deps \
    	-r requirements-macos.txt
	.venv/bin/python3 -m uv pip install .  # <- the app/pkg itself
	@touch $@

dev: .make/dev-deps-installed
.make/dev-deps-installed: requirements-dev-macos.txt
	.venv/bin/python3 -m uv pip install \
    	-r requirements-dev-macos.txt \
    	--editable .  # <- the app/pkg itself
	# If we are updating tools update aws-cdk too
	npm install -g aws-cdk
	@touch $@

# ==================== QUALITY ASSURANCE (CI) ====================

fix: .make/dev-deps-installed
	# Formatting
	.venv/bin/ruff format .
	.venv/bin/isort src/ tests/ scripts

	# Lint Fix
	.venv/bin/ruff check src/ --fix

	# Precommit validations checks
	.venv/bin/pre-commit run
	
	# Final isort to enforce import headings not yet supported in ruff
	.venv/bin/isort src/ test/ scripts

typecheck: .make/dev-deps-installed
	.venv/bin/mypy src

docs: .make/dev-deps-installed
	.venv/bin/md_toc --in-place github --header-levels 4 README.md guides/*.md
	npx cdk-dia --rendering "graphviz-png" --target infra/docs/diagrams/diagram-simple.png --collapse true --collapse-double-clusters true
	npx cdk-dia --rendering "graphviz-png" --target infra/docs/diagrams/diagram-detailed.png --collapse false --collapse-double-clusters false
	npx cdk-dia --rendering "cytoscape-html" --target infra/docs/diagrams/ --collapse false --collapse-double-clusters false    

test: .make/dev-deps-installed
	.venv/bin/python3 -m pytest

wheel:
	.venv/bin/python3 -m build --wheel --installer uv

run: .make/dev-deps-installed
	.venv/bin/python3 -m ${APP_NAME_SNAKE} --voice Matthew --duration 10 --provider bedrock 
	.venv/bin/python3 -m ${APP_NAME_SNAKE} --voice Matthew --duration 10 --provider openai --model gpt-4o
	# .venv/bin/python3 -m ${APP_NAME_SNAKE} --voice Ruth --duration 1
	# .venv/bin/python3 -m ${APP_NAME_SNAKE} --voice Amy --duration 1

serve:
	.venv/bin/python3 -m http.server -d dist

# ==================== PACKAGING / DEPLOYMENT (CD) ====================

docker-login: 
	aws --profile $(AWS_PROFILE) ecr get-login-password --region $(AWS_ECR_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_ECR_REGION).amazonaws.com

docker-clean:
	docker buildx prune -a -f
	docker image prune -f

docker-build: 
	docker buildx build \
		--build-arg TARGET_PYTHON_VERSION=$(DOCKER_PYTHON_BASE) \
		--build-arg PROJECT_NAME=$(APP_NAME_SNAKE) \
		--progress plain \
		-t $(APP_NAME_KEBAB):latest \
		-t $(ECR_REPOSITORY):latest \
		-f containers/docker/Dockerfile \
		.
	docker tag $(APP_NAME_KEBAB):latest $(ECR_REPOSITORY):latest

docker-run:
	docker run -i -t --env-file .env $(APP_NAME_KEBAB)

docker-push: docker-build docker-login
	docker push $(ECR_REPOSITORY):latest


# ==================== INFRASTRUCTURE (IaC) ====================

cdk-diff:
	cdk diff

cdk-synth:
	cdk synth

cdk-deploy: cdk-synth docs
	cdk deploy

cdk-outputs:
	aws cloudformation describe-stacks > cdk.out/cdk-outputs-$(AWS_PROFILE).json

cdk-destroy:
	cdk destroy

# ==================== TEARDOWN ====================
clean:
	rm -rfv .make/
	rm -rfv $(REQUIRED_DIRS)
	rm -rfv .venv
	rm -rfv requirements*.txt
	rm -rfv src/${APP_NAME_SNAKE}.egg-info
	rm -rfv dist/
	docker image prune -f
	docker buildx prune -f
	