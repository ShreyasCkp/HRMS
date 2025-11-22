import os
import sys
from pathlib import Path

# ---------- DEBUG LOGS ----------
try:
    print("WSGI: starting wsgi.py")
except Exception:
    # If stdout is not available, ignore
    pass

# Project root (where manage.py lives)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Our custom site-packages folder created by GitHub Actions
site_packages = ROOT_DIR / ".python_packages" / "lib" / "site-packages"

try:
    print(f"WSGI: ROOT_DIR = {ROOT_DIR}")
    print(f"WSGI: site_packages path = {site_packages}")
    print(f"WSGI: site_packages.exists() = {site_packages.exists()}")
except Exception:
    pass

if site_packages.exists():
    sys.path.insert(0, str(site_packages))
    try:
        print("WSGI: .python_packages/lib/site-packages added to sys.path")
        print("WSGI: first 5 sys.path entries:", sys.path[:5])
    except Exception:
        pass
else:
    try:
        print("WSGI WARNING: .python_packages/lib/site-packages DOES NOT EXIST")
    except Exception:
        pass

from django.core.wsgi import get_wsgi_application

# On Azure → set DJANGO_ENV=deployment
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()
try:
    print(f"WSGI: DJANGO_ENV = {DJANGO_ENV}")
except Exception:
    pass

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
