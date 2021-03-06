from .base import *
from ._sentry import sentry_init

# See `itou.utils.new_dns.middleware.NewDnsRedirectMiddleware`.
ALLOWED_HOSTS = [
    "itou-prod.cleverapps.io",
    "inclusion.beta.gouv.fr",
    "emploi.inclusion.beta.gouv.fr",
    "emplois.inclusion.beta.gouv.fr",
]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ.get("POSTGRESQL_ADDON_DIRECT_HOST"),
        "PORT": os.environ.get("POSTGRESQL_ADDON_DIRECT_PORT"),
        "NAME": os.environ.get("POSTGRESQL_ADDON_DB"),
        "USER": os.environ.get("POSTGRESQL_ADDON_CUSTOM_USER"),
        "PASSWORD": os.environ.get("POSTGRESQL_ADDON_CUSTOM_PASSWORD"),
    }
}

ITOU_ENVIRONMENT = "PROD"
ITOU_PROTOCOL = "https"
ITOU_FQDN = "emplois.inclusion.beta.gouv.fr"
ITOU_EMAIL_CONTACT = "contact@inclusion.beta.gouv.fr"
DEFAULT_FROM_EMAIL = "noreply@inclusion.beta.gouv.fr"

sentry_init(dsn=os.environ["SENTRY_DSN_PROD"])

ALLOW_POPULATING_METABASE = True
