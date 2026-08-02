FROM alpine:3.18

# Refresh package index and install Python, pip, Postgres client libraries, and build tools
RUN apk update && apk upgrade && apk add --no-cache \
    python3 \
    py3-pip \
    postgresql-client \
    postgresql-dev \
    build-base \
    bash \
    curl \
    libffi-dev \
    openssl-dev \
    && ln -sf python3 /usr/bin/python \
    && pip install --upgrade pip

WORKDIR /app

# Install Airflow with Postgres support (Python 3.11 constraints)
RUN pip install "apache-airflow[postgres]==2.9.1" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-3.11.txt"

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
