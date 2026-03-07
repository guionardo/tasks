# Cross-platform Makefile for Linux and Windows (via WSL/Git Bash)
# For native Windows, use Makefile.ps1 PowerShell script

GOBIN ?= $$(go env GOPATH)/bin
UNAME_S := $(shell uname -s 2>/dev/null || echo "Windows")
OS := $(shell echo $(UNAME_S) | tr '[:upper:]' '[:lower:]')

ifneq ($(OS),linux)
$(error This Makefile can only be executed on Linux)
endif

# Detect package manager
ifeq ($(OS),linux)
	PKG_MGR := $(shell which apt-get >/dev/null 2>&1 && echo "apt" || which yum >/dev/null 2>&1 && echo "yum" || which apk >/dev/null 2>&1 && echo "apk" || echo "unknown")
endif

help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)



##@ Dependencies

setup: ## Setup the project
	@echo  "\n🛠️  \033[30;42m SETUPING PROJECT \033[0m"
	@uv sync
	@echo "✅  pre commit setup"
	@pre-commit autoupdate
	@pre-commit install -t commit-msg -t pre-commit || echo "⚠️  Pre-commit hooks installation skipped (may need manual setup)"
	@echo "✅  PROJECT SETUP"






install-commitlint:
	@echo  "\n🛠️  \033[30;42m INSTALLING COMMITLINT \033[0m"
	@go install github.com/conventionalcommit/commitlint@latest
	@if ! command -v commitlint >/dev/null 2>&1; then \
		echo "commitlint not found or not accessible yet."; \
		exit 1; \
	fi
	@if [ ! -f .commitlint.yml ] && [ ! -f .commitlint.yaml ] && [ ! -f commitlint.yml ] && [ ! -f commitlint.yaml ]; then \
		echo "\n  No commitlint config file found."; \
		read -p "Do you want to create commitlint config? (y/n): " answer && \
		if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
			echo "Creating commitlint config..."; \
			commitlint config create; \
		else \
			echo "Skipping commitlint config creation."; \
		fi; \
	fi
	@echo "✅  COMMITLINT INSTALLED"



##@ Testing

test: ## Run tests
	@echo  "\n🛠️  \033[30;42m RUNNING TESTS \033[0m"
	@uv run pytest -q -vvv



##@ Release

increment-minor: ## Increment version (minor)
	@echo  "\n🛠️  \033[30;42m INCREMENTING VERSION \033[0m"
	@read -p "Confirm version increment $$(uv version --bump minor --dry-run)? (y/n): " answer && \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		uv version --bump minor ; \
	else \
		echo "Skipping version increment."; \
	fi;

increment-patch: ## Increment version (patch)
	@echo  "\n🛠️  \033[30;42m INCREMENTING VERSION \033[0m"
	@read -p "Confirm version increment $$(uv version --bump patch --dry-run)? (y/n): " answer && \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		uv version --bump patch ; \
	else \
		echo "Skipping version increment."; \
	fi;

publish: ## Publish to PyPI
	@if [ "$$UV_PUBLISH_USERNAME" = "" ] || [ "$$UV_PUBLISH_PASSWORD" = "" ]; then \
		echo "UV_PUBLISH_USERNAME or UV_PUBLISH_PASSWORD is not set"; \
		exit 1; \
	fi;
	@uv build
	@echo  "\n🛠️  \033[30;42m PUBLISHING TO PYPI \033[0m"
	@read -p "Confirm publish? (y/n): " answer && \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		uv publish ; \
	else \
		echo "Skipping publish."; \
	fi;

##@ Installation and Release

install: ## Install the package locally
	uv tool install .

# release:
#     bash .github/scripts/release.sh
