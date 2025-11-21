#!/usr/bin/env bash
# start.sh - run migrations, collectstatic and start gunicorn
set -euo pipefail

# Default settings module if not provided
: "${DJANGO_SETTINGS_MODULE:=smarthr_erp.deployment}"
export DJANGO_SETTINGS_MODULE

echo "Starting container with DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"

# Wait for DB host to become available (if DB_HOST set), fallback to retry with migrate logic
DB_HOST=${DB_HOST:-}
DB_PORT=${DB_PORT:-5432}
MAX_TRIES=${MAX_TRIES:-30}
SLEEP_SECONDS=${SLEEP_SECONDS:-2}

if [ -n "$DB_HOST" ]; then
  echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
  tries=0
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    tries=$((tries+1))
    echo "Database not up yet (attempt ${tries}/${MAX_TRIES}) — sleeping ${SLEEP_SECONDS}s..."
    if [ "$tries" -ge "$MAX_TRIES" ]; then
      echo "Timed out waiting for database at ${DB_HOST}:${DB_PORT}"
      exit 1
    fi
    sleep "$SLEEP_SECONDS"
  done
  echo "Database reachable."
fi

# Run migrations with retries (covers transient DB startup)
i=0
until python manage.py migrate --noinput 2>/tmp/migrate.err; do
  i=$((i+1))
  echo "migrate failed (attempt $i/$MAX_TRIES). Sleeping ${SLEEP_SECONDS}s and retrying..."
  cat /tmp/migrate.err || true
  if [ "$i" -ge "$MAX_TRIES" ]; then
    echo "Migrations failed after $MAX_TRIES attempts. Exiting."
    exit 1
  fi
  sleep $SLEEP_SECONDS
done

echo "Migrations applied."

# Collect static files
python manage.py collectstatic --noinput
echo "Collectstatic finished."

# Optionally create superuser if env var provided (non-interactive)
if [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ] && [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  echo "Creating superuser (if not exists)..."
  python manage.py shell -c "from django.contrib.auth import get_user_model; User=get_user_model(); \
username='${DJANGO_SUPERUSER_USERNAME}'; \
email='${DJANGO_SUPERUSER_EMAIL}'; \
pw='${DJANGO_SUPERUSER_PASSWORD}'; \
User.objects.filter(username=username).exists() or User.objects.create_superuser(username, email, pw)"
fi

# Start Gunicorn
PORT=${PORT:-8000}
WORKERS=${GUNICORN_WORKERS:-3}
echo "Starting Gunicorn on 0.0.0.0:${PORT} with ${WORKERS} workers"
exec gunicorn smarthr_erp.wsgi:application --bind 0.0.0.0:${PORT} --workers ${WORKERS} --timeout 120
