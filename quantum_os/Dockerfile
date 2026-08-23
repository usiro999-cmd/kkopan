FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
ARG QUANTUM_UID=1000
ARG QUANTUM_GID=1000

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/quantum/bin:/home/quantum/.local/bin:$PATH

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        git \
        libgomp1 \
        python3 \
        python3-venv \
        tini \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    existing_group="$(getent group "${QUANTUM_GID}" | cut -d: -f1 || true)"; \
    if [ -n "${existing_group}" ] && [ "${existing_group}" != "quantum" ]; then \
        groupmod --new-name quantum "${existing_group}"; \
    elif [ -z "${existing_group}" ]; then \
        groupadd --gid "${QUANTUM_GID}" quantum; \
    fi; \
    existing_user="$(getent passwd "${QUANTUM_UID}" | cut -d: -f1 || true)"; \
    if [ -n "${existing_user}" ] && [ "${existing_user}" != "quantum" ]; then \
        usermod --login quantum --home /home/quantum \
            --move-home "${existing_user}"; \
        usermod --gid quantum --shell /bin/bash quantum; \
    elif [ -z "${existing_user}" ]; then \
        useradd --uid "${QUANTUM_UID}" --gid quantum --create-home \
            --shell /bin/bash quantum; \
    fi; \
    usermod --groups '' quantum; \
    python3 -m venv /opt/quantum; \
    chown -R quantum:quantum /opt/quantum /home/quantum

COPY requirements.txt /tmp/requirements.txt
RUN /opt/quantum/bin/python -m pip install --no-cache-dir --upgrade pip \
    && /opt/quantum/bin/python -m pip install \
        --no-cache-dir --requirement /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY --chmod=755 bin/quantum-info /usr/local/bin/quantum-info
COPY --chmod=755 bin/start-quantum-os /usr/local/bin/start-quantum-os
COPY --chown=quantum:quantum examples /opt/quantum-os/examples

RUN mkdir -p /workspace \
    && chown quantum:quantum /workspace \
    && su quantum -c "/opt/quantum/bin/python -m ipykernel install \
        --user --name quantum-os --display-name 'Quantum OS (Python)'"

USER quantum
WORKDIR /workspace

EXPOSE 8888
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/start-quantum-os"]
CMD []

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl --fail --silent \
        "http://127.0.0.1:8888/api/status?token=${JUPYTER_TOKEN}" >/dev/null \
        || exit 1
