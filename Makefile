SHELL := /bin/bash

# Include environment file
# Includes env variables required for the application !(ENV var is also defined here)
-include .env
# set value to ENV env var, defaults to dev
ENV ?= dev
-include environments/$(ENV).env

# Some util vars
## A random small hash to use if required using the last commit hash
HASH := $(shell git rev-parse --short HEAD)

# Clean up
clean:
	rm -rf .venv

# Install project dependencies (requires uv installed)
install:
	@uv sync --locked --all-extras --dev

# Runs the app project entrypoint
run:
	@uv run uvicorn main:app --reload --port 8080

# Runs pytest cases in tests/
test:
	@uv run pytest \
		--cov=src \
		--cov-config=.coveragerc \
		--cov-report=term-missing \
		--cov-report=xml \
		tests/

# Generates the html coverage report
test-html:
	@uv run pytest \
		--cov=src \
		--cov-config=.coveragerc \
		--cov-report=term-missing \
		--cov-report=html \
		tests/

# Local build and run of the docker container
build-local:
	docker build -t $(IMAGE_NAME) .

run-build-local:
	docker run --env-file .env -p $(PORT):$(PORT) $(IMAGE_NAME)

# GCP build, push and deploy functions
## Compute IMAGE_NAME based on ENV
## compute-image-name = $(if $(filter pro,$(ENV)),$(IMAGE_NAME)-$(shell git config user.name)-$(HASH),$(IMAGE_NAME))

## Builds and pushes to the Artifact Registry (Requires prior gcloud docker setup)
build-and-push:
	@echo "Using image name: $(IMAGE_NAME)"
	@gcloud auth configure-docker $(AR_REGION)-docker.pkg.dev
	@export TAG="$(AR_REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/$(IMAGE_NAME)" && \
	echo "TAG = $$TAG" && \
	docker buildx build --platform linux/amd64 --provenance false -t "$$TAG" --push .

## Deploys new revision for the Cloud Run service
deploy:
	@echo "Deploying image: $(IMAGE_NAME) - to Cloud run $(CLOUD_RUN_NAME)"
	@ENV_VARS=$$(grep -v '^#' .env \
		| grep -v '^ENV=' \
		| grep -v '^GOOGLE_APPLICATION_CREDENTIALS=' \
		| grep -v '^PORT=' \
		| xargs \
		| sed 's/ /,/g'); \
	gcloud run deploy $(CLOUD_RUN_NAME) \
		--project=$(PROJECT_ID) \
		--region=$(CLOUD_RUN_REGION) \
		--image=$(AR_REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_NAME)/$(IMAGE_NAME) \
		--platform=managed \
		--port=$(PORT) \
		--set-env-vars=$$ENV_VARS \
		--service-account=$(SERVICE_ACCOUNT_EMAIL) \
		--quiet
	@SERVICE_URL=$$(gcloud run services describe $(CLOUD_RUN_NAME) \
		--project=$(PROJECT_ID) \
		--region=$(CLOUD_RUN_REGION) \
		--format='value(status.url)'); \
	echo "✅ Deployed successfully! Service URL: $$SERVICE_URL"
