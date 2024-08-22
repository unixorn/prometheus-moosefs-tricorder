.PHONY: all c clean \
	f format \
	h help \
	local \
	multiarch_image \
	publish \
	t test \
	wheel

h: help
c: clean
f: format
t: test

help:
	@echo "Options:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

HUB_USER=unixorn
MOOSEFS_VERSION=3.116
PLATFORMS=linux/arm64,linux/amd64,linux/arm/v7

requirements.txt: poetry.lock pyproject.toml Makefile
	poetry export -o requirements.txt

format:
	black moosefs_tricorder tests

install_hooks: ## Install the git hooks
	poetry run pre-commit install

local: wheel requirements.txt ## Makes a moosefs-tricorder docker image for only the architecture we're running on. Does not push to dockerhub.
	docker buildx build --build-arg application_version=${MOOSEFS_VERSION} --pull --load -t ${HUB_USER}/moosefs-tricorder:latest -f Dockerfile.dev .

multiarch: local ## Makes a moosefs-tricorder multi-architecture docker image for linux/arm64, linux/amd64 and linux/arm/v7 and pushes it to dockerhub
	docker buildx build --build-arg application_version=${MOOSEFS_VERSION} --platform ${PLATFORMS} --pull --push -t ${HUB_USER}/moosefs-tricorder:$(MOOSEFS_VERSION) -f Dockerfile .
	docker buildx build --build-arg application_version=${MOOSEFS_VERSION} --platform ${PLATFORMS} --pull --push -t ${HUB_USER}/moosefs-tricorder:latest -f Dockerfile .
	docker buildx build --build-arg application_version=${MOOSEFS_VERSION} --pull --load -t ${HUB_USER}/moosefs-tricorder:latest -f Dockerfile .

wheel: format # Bake a wheel file
	poetry build
