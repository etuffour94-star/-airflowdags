FROM alpine:3.18

RUN apk update && apk upgrade && apk add --no-cache \
    python3 \
    python3-dev \
    py3-pip \
    py3-pybind11-dev \
    postgresql-client \
    postgresql-dev \
    build-base \
    bash \
    curl \
    libffi-dev \
    openssl-dev \
    linux-headers \
    abseil-cpp-dev \
    re2-dev \
    && ln -sf python3 /usr/bin/python \
    && pip install --upgrade pip

WORKDIR /app

RUN pip install "apache-airflow[postgres]==2.9.1" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.9.1/constraints-3.11.txt"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]