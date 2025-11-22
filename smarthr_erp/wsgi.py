import os
import sys
from pathlib import Path

# === 1. Point to project root (where manage.py is) ===
ROOT_DIR = Path(__file__).resolve().parent.parent  # smarthr_erp/ -> project root

# === 2. Add .python_packages to sys.path (where GitHub Actions installs deps) ===
site_packages = ROOT_DIR / ".python_packages" / "lib" / "site-packages"
if site_packages.exists():
    # Debug print - shows up in Azure logs
    print(">>> Using .python_packages at:", site_packages)
    sys.path.insert(0, str(site_packages))
else:
    print(">>> .python_packages NOT FOUND at:", site_packages)

# === 3. Normal Django WSGI import ===
from django.core.wsgi import get_wsgi_application

# === 4. Environment-based settings selection ===
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()
print(">>> DJANGO_ENV =", DJANGO_ENV)

if DJANGO_ENV == "deployment":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.deployment")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.settings")

print(">>> DJANGO_SETTINGS_MODULE =", os.environ["DJANGO_SETTINGS_MODULE"])

application = get_wsgi_application()
print(">>> WSGI application loaded successfully")
