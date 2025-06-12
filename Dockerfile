FROM node:20.13.1-alpine AS frontend

WORKDIR /app/frontend
COPY frontend/ ./
RUN npm install -g @quasar/cli && npm install
RUN quasar build

FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS sys_setup

RUN apt-get update \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY uv.lock ./
COPY pyproject.toml ./

RUN uv sync --frozen --no-install-project --no-dev

FROM sys_setup AS final

COPY --from=sys_setup /app/backend/.venv /opt/venv
COPY --from=frontend /app/backend/static /app/backend/static
COPY --from=frontend /app/backend/static/index.html /app/backend/templates/index.html

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/backend

COPY backend/ ./

RUN adduser --disabled-password --gecos '' rapuser

RUN python manage.py collectstatic --noinput --clear

# CMD ["python", "manage.py", "migrate", ";", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
CMD ["sh", "-c", "python manage.py migrate ; gunicorn config.wsgi:application --bind 0.0.0.0:8000 --log-level DEBUG"]
# CMD ["sh", "-c", "python manage.py migrate ; python manage.py runserver"]

