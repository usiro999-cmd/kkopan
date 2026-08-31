FROM python:3.12-slim AS runtime

ARG SERVICE_PATH

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/services/common:/app/service

WORKDIR /app

COPY pyproject.toml ./
COPY services/common ./services/common
RUN pip install --no-cache-dir .

COPY ${SERVICE_PATH} ./service

USER 65532:65532

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
