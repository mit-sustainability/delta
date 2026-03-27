.PHONY: setup init-db dev test dbt-deps dbt-build-local dbt-build-prod load-local-raw docker-build clean

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

dbt-build-local:
	cd dbt && DBT_TARGET=local $(UV) run dbt build

dbt-build-prod:
	cd dbt && DBT_TARGET=prod $(UV) run dbt build

load-local-raw:
	@test -n "$(RAW_CSV_PATH)" || (echo "RAW_CSV_PATH is required" >&2; exit 1)
	@test -n "$(RAW_TABLE)" || (echo "RAW_TABLE is required" >&2; exit 1)
	$(UV) run python scripts/load_local_raw_csv.py --csv "$(RAW_CSV_PATH)" --table "$(RAW_TABLE)"

docker-build:
	docker build -t delta-platform:latest .

clean:
	rm -rf $(VENV)
	rm -rf .dagster
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "target" -exec rm -rf {} +
