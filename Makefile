.PHONY: install test lint images demo api web

install:
	python -m pip install -e '.[dev]'

lint:
	ruff check src tests tools

test:
	pytest

images:
	docker build -f docker/patcher.Dockerfile -t rescuebench/patcher:local .
	docker build -f docker/python.Dockerfile -t rescuebench/python:local .
	docker build -f docker/node.Dockerfile -t rescuebench/node:local .
	docker build -f docker/config.Dockerfile -t rescuebench/config:local .

demo: images
	rescuebench agent py-fastapi-tenant-leak --provider mock

api:
	rescuebench serve

web:
	cd web && npm run dev
