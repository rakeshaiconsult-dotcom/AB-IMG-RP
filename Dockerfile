FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    cron \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirement.txt

COPY . .

RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

RUN mkdir -p /app/email_attachments /app/output && \
    chmod -R 755 /app/email_attachments /app/output

RUN touch /var/log/cron.log && \
    chmod 0644 /var/log/cron.log

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Kolkata

VOLUME ["/app/email_attachments", "/app/output", "/app/logs"]

ENTRYPOINT ["/app/entrypoint.sh"]
