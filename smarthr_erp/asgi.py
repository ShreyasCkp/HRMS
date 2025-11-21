import os
from django.core.wsgi import get_wsgi_application

# If DJANGO_SETTINGS_MODULE is explicitly set (Azure/App Service/Gunicorn), use it.
# Otherwise default to 'smarthr_erp.deployment' when DEBUG=False in env, else use base settings.
if "DJANGO_SETTINGS_MODULE" not in os.environ:
    # try to read DEBUG from .env if present so local testing with DEBUG=False uses deployment
    # but avoid importing django/environ here — keep simple: check env var DEBUG
    debug_env = os.environ.get("DEBUG", "True")
    if debug_env.lower() in ("false", "0", "no"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.deployment")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.settings")
else:
    # honor whatever the environment provided (Azure sets this normally)
    pass

application = get_wsgi_application()
