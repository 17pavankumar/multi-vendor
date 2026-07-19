# Development image — bind-mounted over in docker-compose.yml so code
# changes on the host are picked up without a rebuild. A separate,
# multi-stage Dockerfile.prod (no bind mount, no runserver) belongs in
# a later phase once we're deploying rather than developing.
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout — both
# matter for `docker compose logs` to show output as it happens.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# mysqlclient (the requirements.txt driver) compiles against libmysqlclient
# at install time, so the dev headers must be present before `pip install`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copied and installed before the rest of the source so Docker's layer
# cache can skip this (slow) step on rebuilds that only change app code.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
