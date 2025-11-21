# Dockerfile - production image for local testing & Azure container
FROM python:3.11-slim

# avoid interactive prompts during apt installs
ENV DEBIAN_FRONTEND=noninteractive

# system deps for psycopg2, pycairo, weasyprint-ish libs and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    libglib2.0-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    gcc \
    curl \
    git \
    gettext \
    ca-certificates \
    netcat \
  && rm -rf /var/lib/apt/lists/*

# Create app user
ENV APP_USER=app
RUN adduser --disabled-password --gecos "" $APP_USER

WORKDIR /app

# Copy requirements first to take advantage of Docker layer caching
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install wheel to avoid build issues
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy code
COPY . /app

# Ensure start script is executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Change ownership and switch to non-root user
RUN chown -R $APP_USER:$APP_USER /app /start.sh
USER $APP_USER

ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
