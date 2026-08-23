FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --system updater \
    && useradd --system --gid updater --home /app updater

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY app ./app
COPY tests ./tests
COPY pytest.ini .
RUN mkdir -p /var/lib/quantum-updater \
    && chown -R updater:updater /app /var/lib/quantum-updater

# Docker socket access is granted at runtime. The updater is isolated from the
# quantum workload and only accepts signed, allow-listed image manifests.
USER updater
EXPOSE 9090
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9090"]

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9090/health')" \
        || exit 1
