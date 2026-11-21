FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ethtool \
        iproute2 \
        iputils-ping \
        libpcap0.8 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY netpulse ./netpulse

RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["netpulse"]
