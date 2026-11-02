# syntax=docker/dockerfile:1

# Base image pinned by digest. Bump deliberately: docker pull python:3.12-slim, then copy the digest from
#   docker image inspect python:3.12-slim --format '{{index .RepoDigests 0}}'
ARG PYTHON_IMAGE=python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1

# ---- build stage: compile deps (and bake any models/downloads, verified with sha256sum -c) ----
FROM ${PYTHON_IMAGE} AS builder

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential \
 && rm -rf /var/lib/apt/lists/*

ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN python -m venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH

COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- runtime stage: no compilers, non-root ----
FROM ${PYTHON_IMAGE}

RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin app

COPY --from=builder /opt/venv /opt/venv
COPY app /srv/app

WORKDIR /srv
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--no-server-header", \
     "--limit-concurrency", "100", "--timeout-keep-alive", "5"]
