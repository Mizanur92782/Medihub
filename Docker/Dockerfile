FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/Docker/entrypoint.sh && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R app:app /app

USER app

ENTRYPOINT [ "sh", "/app/Docker/entrypoint.sh" ]
