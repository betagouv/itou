from .base import *  # noqa

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


ALLOWED_HOSTS = ["inclusion.beta.gouv.fr"]

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": os.environ.get("POSTGRESQL_ADDON_DIRECT_HOST"),
        "PORT": os.environ.get("POSTGRESQL_ADDON_DIRECT_PORT"),
        "NAME": os.environ.get("POSTGRESQL_ADDON_DB"),
        "USER": os.environ.get("POSTGRESQL_ADDON_USER"),
        "PASSWORD": os.environ.get("POSTGRESQL_ADDON_PASSWORD"),
    }
}

ITOU_PROTOCOL = "https"
ITOU_FQDN = "inclusion.beta.gouv.fr"
ITOU_EMAIL_CONTACT = "contact@inclusion.beta.gouv.fr"
DEFAULT_FROM_EMAIL = "noreply@inclusion.beta.gouv.fr"

sentry_sdk.init(dsn=os.environ["SENTRY_DSN_PROD"], integrations=[DjangoIntegration()])
