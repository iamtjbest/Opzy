# Opzy backend (FastAPI + Postgres via SQLAlchemy/asyncpg).
#
# Two stages: build deps into a venv, then copy just the venv and source into a slim
# runtime image. Render passes $PORT at runtime — bind to it, not a hardcoded port.

FROM python:3.11-slim AS build

WORKDIR /app

# Needed to build argon2 (pwdlib[argon2]) and asyncpg wheels on slim.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim AS runtime

WORKDIR /app

# libpq isn't needed (asyncpg is pure-Python + C extension bundled in its wheel), so the
# runtime image stays slim with no build toolchain.
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

# Runs as non-root.
RUN useradd --create-home --uid 1000 appuser
USER appuser

EXPOSE 8000

# Migrations run as a separate Render "pre-deploy" command (see render.yaml), not here —
# baking them into the image start command would re-run them on every restart/scale
# event, not just on deploy.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
