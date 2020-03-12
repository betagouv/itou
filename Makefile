# Global tasks.
# =============================================================================

.PHONY: run black clean cdsitepackages pylint check_code_quality

# Run a local server.
run:
	docker-compose -f docker-compose-dev.yml up

clean:
	find . -type d -name "__pycache__" -depth -exec rm -rf '{}' \;

cdsitepackages:
	docker exec -ti -w /usr/local/lib/python3.7/site-packages itou_django /bin/bash

black:
	docker exec -ti itou_django black itou/

pylint:
	docker exec -ti itou_django pylint --rcfile='.pylintrc' --reports=no --output-format=colorized 'itou';

check_code_quality: black pylint

prepare_cc_secrets:
	# Merge secrets
	cat envs/dev.env > envs/cc.env
	cat envs/secrets.env > envs/cc.env
	# Convert into Base64 files
	base64 envs/cc.env  | tr -d \\n > envs/base64/cc.env

# Django.
# =============================================================================

.PHONY: django_admin populate_db

# make django_admin
# make django_admin COMMAND=dbshell
# make django_admin COMMAND=createsuperuser
# make django_admin COMMAND="dumpdata siaes.Siae" > ~/Desktop/siaes.json
django_admin:
	docker exec -ti itou_django django-admin $(COMMAND)

populate_db:
	make django_admin COMMAND="import_cities"
	make django_admin COMMAND="loaddata itou/fixtures/jobs.json"
	make django_admin COMMAND="loaddata itou/fixtures/siaes.json"
	make django_admin COMMAND="loaddata itou/fixtures/prescribers.json"
	make django_admin COMMAND="loaddata itou/fixtures/test_users.json"
	make django_admin COMMAND="loaddata itou/fixtures/prescriber_memberships.json"
	make django_admin COMMAND="loaddata itou/fixtures/siae_memberships.json"

# Tests.
# =============================================================================

.PHONY: test

# make test
# make test TARGET=itou.utils
# make test TARGET=itou.utils.tests.UtilsTemplateTagsTestCase.test_url_add_query
test:
	docker exec -ti itou_django django-admin test --settings=config.settings.test --noinput --failfast --parallel=2 $(TARGET)

# Docker shell.
# =============================================================================

.PHONY: shell_on_django_container shell_on_django_container_as_root shell_on_postgres_container

shell_on_django_container:
	docker exec -ti itou_django /bin/bash

shell_on_django_container_as_root:
	docker exec -ti --user root itou_django /bin/bash

shell_on_postgres_container:
	docker exec -ti itou_postgres /bin/bash

# Postgres CLI.
# =============================================================================

.PHONY: psql_itou psql_root

# Connect to the `itou` database as the `itou` user.
psql_itou:
	docker exec -ti -e PGPASSWORD=password itou_postgres psql -U itou -d itou

# Connect to postgres client as the `root` user.
psql_root:
	docker exec -ti -e PGPASSWORD=password itou_postgres psql -U postgres

# Postgres (backup / restore).
# Inspired by:
# https://cookiecutter-django.readthedocs.io/en/latest/docker-postgres-backups.html
# =============================================================================

.PHONY: postgres_backup postgres_backups_cp_locally postgres_backups_list postgres_backup_restore postgres_backups_clean

postgres_backup:
	docker-compose -f docker-compose-dev.yml exec postgres backup

postgres_backups_cp_locally:
	docker cp itou_postgres:/backups ~/Desktop/backups

postgres_backups_list:
	docker-compose -f docker-compose-dev.yml exec postgres backups

# Note: Django must be stopped to avoid a "database "itou" is being accessed by other users" error.
# make postgres_backup_restore FILE=backup_2019_10_08T12_33_00.sql.gz
postgres_backup_restore:
	docker-compose -f docker-compose-dev.yml up -d --no-deps postgres && \
	docker-compose -f docker-compose-dev.yml exec postgres restore $(FILE) && \
	docker-compose -f docker-compose-dev.yml stop

postgres_backups_clean:
	docker-compose -f docker-compose-dev.yml exec postgres clean

# Delete and recreate the DB manually.
# =============================================================================
# docker-compose -f docker-compose-dev.yml down
# docker-compose -f docker-compose-dev.yml up --no-deps postgres
# make shell_on_postgres_container
# PGPASSWORD=password psql -h postgres -U postgres
# DROP DATABASE itou;
# CREATE DATABASE itou OWNER itou;
