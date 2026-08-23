FROM python:3.12-slim AS builder

COPY requirements.txt /tmp/requirements.txt
RUN mkdir -p /payload/site-packages \
    && python -m pip install --no-cache-dir \
        --target /payload/site-packages \
        --requirement /tmp/requirements.txt

COPY python /payload/site-packages
COPY kernel /payload/share/jupyter/kernels/multiverse-ai
COPY examples /payload/examples

FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install --yes --no-install-recommends coreutils \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /payload /payload
COPY --chmod=755 install-pack /usr/local/bin/install-pack
ENTRYPOINT ["/usr/local/bin/install-pack"]
