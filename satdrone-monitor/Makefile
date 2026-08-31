.PHONY: bootstrap dev down logs test validate

bootstrap:
	cp -n .env.example .env || true
	cd apps/web && npm install

dev:
	docker compose up --build

down:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

test:
	python -m pytest services
	cd apps/web && npm test -- --run

validate:
	docker compose config --quiet
	python -m compileall -q services
	cd apps/web && npm run build

