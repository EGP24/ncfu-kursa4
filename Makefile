.PHONY: backend-setup backend-lock backend-install backend-run backend-test backend-lint backend-typecheck backend-check
.PHONY: frontend-install frontend-run frontend-build frontend-test frontend-e2e frontend-all
.PHONY: docker-up docker-down docker-logs docker-build

backend-setup:
	$(MAKE) -C backend setup

backend-lock:
	$(MAKE) -C backend lock

backend-install:
	$(MAKE) -C backend install

backend-run:
	$(MAKE) -C backend run

backend-test:
	$(MAKE) -C backend test

backend-lint:
	$(MAKE) -C backend lint ARGS="$(ARGS)"

backend-typecheck:
	$(MAKE) -C backend typecheck

backend-check:
	$(MAKE) -C backend check

frontend-install:
	npm --prefix frontend install

frontend-run:
	npm --prefix frontend run dev

frontend-build:
	npm --prefix frontend run build

frontend-test:
	npm --prefix frontend run test

frontend-e2e:
	sh -c 'npm --prefix frontend run dev -- --port 3100 --no-open > /tmp/frontend-dev.log 2>&1 & DEV_PID=$$!; trap "kill $$DEV_PID" EXIT; for i in $$(seq 1 120); do if curl -sSf "http://localhost:3100/login" > /dev/null; then break; fi; sleep 1; done; npm --prefix frontend run test:e2e -- --config baseUrl=http://localhost:3100'

frontend-all: frontend-install frontend-test frontend-build frontend-e2e

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build
