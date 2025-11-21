# Dockerfile - production image for local testing & Azure container
FROM python:3.11-slim

# system deps for psycopg2, build tools and basic utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    gettext \
    ca-certificates \
    netcat \
  && rm -rf /var/lib/apt/lists/*

# Create app user
ENV APP_USER=app
RUN adduser --disabled-password --gecos "" $APP_USER

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY . /app

# Ensure start script is executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Use non-root
RUN chown -R $APP_USER:$APP_USER /app /start.sh
USER $APP_USER

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
