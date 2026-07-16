.PHONY: install build-frontend dev-frontend check deploy

DEPLOY_HOST ?=
# no leading ~/ - the shell expands ~ locally before make sees it
DEPLOY_PATH ?= klipper-cam-sight

install:
	bash install.sh

build-frontend:
	cd frontend && npm ci && npm run build

dev-frontend:
	cd frontend && bash -c 'set -a; [ -f ../.env ] && . ../.env; set +a; npm run dev'

check:
	python3 install.py --check
	python3 -c "import sys; sys.path.insert(0,'.'); \
	from lib.geometry import _self_check; \
	from lib.session import _self_check as _s; \
	from lib import tool_backend; \
	from lib.cache import _self_check as _c; \
	from lib.klippy_probe import _self_check as _p; \
	_s(); _c(); _p()"

deploy: build-frontend
	@test -n "$(DEPLOY_HOST)" || (echo "Set DEPLOY_HOST, e.g. pi@printer" && exit 1)
	rsync -avz --delete \
		--exclude 'frontend/node_modules' \
		./ $(DEPLOY_HOST):$(DEPLOY_PATH)/
	@echo "Deployed to $(DEPLOY_HOST):$(DEPLOY_PATH) - ssh in and run: make install"

# Set DEPLOY_HOST (required) and optionally DEPLOY_PATH (default: klipper-cam-sight).
# Path is relative to the remote user's home - do not use ~/ (shell expands it locally).
#   DEPLOY_HOST=pi@printer make deploy
#   DEPLOY_HOST=pi@printer DEPLOY_PATH=klipper-cam-sight make deploy
