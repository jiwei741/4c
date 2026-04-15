FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY infra/docker/backend-runtime-requirements.txt /tmp/backend-runtime-requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 \
    && python -m pip install -r /tmp/backend-runtime-requirements.txt --extra-index-url https://pypi.org/simple

COPY services/backend /app/services/backend
COPY services/inference/run_scenario.py /app/services/inference/run_scenario.py
COPY services/inference/src /app/services/inference/src
COPY services/inference/examples /app/services/inference/examples
COPY services/inference/outputs /app/services/inference/outputs
COPY data/processed /app/data/processed

WORKDIR /app/services/backend

EXPOSE 8000

CMD ["python", "app.py"]
