from .base import *
from ._sentry import sentry_init

INSTALLED_APPS += ["django_dramatiq_pg",]

ALLOWED_HOSTS = ["127.0.0.1", ".cleverapps.io"]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ.get("POSTGRESQL_ADDON_HOST"),
        "PORT": os.environ.get("POSTGRESQL_ADDON_PORT"),
        "NAME": os.environ.get("REVIEW_APP_DB_NAME"),
        "USER": os.environ.get("POSTGRESQL_ADDON_USER"),
        "PASSWORD": os.environ.get("POSTGRESQL_ADDON_PASSWORD"),
    }
}

ITOU_ENVIRONMENT = "REVIEW_APP"
ITOU_PROTOCOL = "https"
ITOU_FQDN = os.environ.get("DEPLOY_URL", "staging.inclusion.beta.gouv.fr")
ITOU_EMAIL_CONTACT = "contact+staging@inclusion.beta.gouv.fr"
DEFAULT_FROM_EMAIL = "noreply+staging@inclusion.beta.gouv.fr"

sentry_init(dsn=os.environ["SENTRY_DSN_STAGING"])

sentry_sdk.init(dsn=os.environ["SENTRY_DSN_STAGING"], integrations=[DjangoIntegration()])
ignore_logger("django.security.DisallowedHost")
SHOW_TEST_ACCOUNTS_BANNER = True

# Database connection data is overriden, so we must repeat this part:
# ---
DRAMATIQ_BROKER = {**DRAMATIQ_BROKER_BASE,
                   "OPTIONS": {"url": f"postgres://{DATABASES[DRAMATIQ_DB_ALIAS]['USER']}:{DATABASES[DRAMATIQ_DB_ALIAS]['PASSWORD']}@{DATABASES[DRAMATIQ_DB_ALIAS]['HOST']}:{DATABASES[DRAMATIQ_DB_ALIAS]['PORT']}/{DATABASES[DRAMATIQ_DB_ALIAS]['NAME']}", }}

# Must be defined after broker
DRAMATIQ_REGISTRY = DRAMATIQ_REGISTRY_BASE