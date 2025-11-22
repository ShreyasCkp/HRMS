import os
import sys
from pathlib import Path

# 👇 Make sure Python can see .python_packages (where GitHub Actions installed deps)
ROOT_DIR = Path(__file__).resolve().parent.parent  # project root (where manage.py is)
site_packages = ROOT_DIR / ".python_packages" / "lib" / "site-packages"
if site_packages.exists():
    sys.path.insert(0, str(site_packages))

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
