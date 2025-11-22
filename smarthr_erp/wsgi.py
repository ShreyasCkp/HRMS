import os
from django.core.wsgi import get_wsgi_application

# Decide settings based on environment variable (like your old project)
# On Azure → set DJANGO_ENV=deployment
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()

if DJANGO_ENV == "deployment":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "smarthr_erp.deployment"
    )
else:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "smarthr_erp.settings"
    )

application = get_wsgi_application()
