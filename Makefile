.PHONY: backend-setup backend-lock backend-install backend-run backend-test backend-lint backend-typecheck backend-check
.PHONY: frontend-install frontend-run frontend-build
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
	$(MAKE) -C backend lint

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

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build
