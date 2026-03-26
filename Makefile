.PHONY: setup init-db dev test dbt-deps docker-build clean

VENV = .venv
UV = uv

setup:
	@echo "Setting up environment with uv..."
	$(UV) sync
	$(UV) run pre-commit install
	@echo "Run 'direnv allow' to activate environment variables."

init-db:
	./scripts/init_db.sh

dev:
	$(UV) run dagster dev

test:
	$(UV) run pytest cockpit/tests

dbt-deps:
	cd dbt && $(UV) run dbt deps

docker-build:
	docker build -t delta-platform:latest .

clean:
	rm -rf $(VENV)
	rm -rf .dagster
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "target" -exec rm -rf {} +
