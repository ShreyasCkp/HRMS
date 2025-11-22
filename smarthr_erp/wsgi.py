import os
import sys
from pathlib import Path

# Resolve project root robustly
# __file__ will be something like:
# - /home/site/wwwroot/smarthr_erp/wsgi.py
#   or
# - /home/site/wwwroot/python-app/smarthr_erp/wsgi.py
WSGI_FILE = Path(__file__).resolve()
PROJECT_DIR = WSGI_FILE.parent              # smarthr_erp
ROOT_DIR = PROJECT_DIR.parent               # project root

# Try a couple of candidate roots: ROOT_DIR and ROOT_DIR.parent
# to handle an extra folder (like python-app/)
candidates = [ROOT_DIR, ROOT_DIR.parent]

site_packages_path = None
for base in candidates:
    p = base / ".python_packages" / "lib" / "site-packages"
    if p.exists():
        site_packages_path = p
        sys.path.insert(0, str(p))
        print(f">>> Using .python_packages at: {p}")
        break

if site_packages_path is None:
    print(">>> .python_packages NOT FOUND in candidates:")
    for base in candidates:
        print(f"    - {base / '.python_packages' / 'lib' / 'site-packages'}")
    print(">>> sys.path (truncated):")
    print(sys.path[:10])

# DJANGO_ENV-based settings selection
DJANGO_ENV = os.getenv("DJANGO_ENV", "local").lower()

if DJANGO_ENV == "deployment":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.deployment")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smarthr_erp.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
