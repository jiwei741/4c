FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
COPY app.py /app/app.py

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "app.py"]
