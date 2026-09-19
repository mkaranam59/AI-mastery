FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    LANGFLOW_CONFIG_DIR=/data

RUN pip install "langflow==1.12.1" "lfx-bundles[groq]==1.1.23" \
    && mkdir -p /data

ENV LANGFLOW_DATABASE_URL=sqlite:////data/langflow.db

WORKDIR /app
EXPOSE 7860

CMD ["sh", "-c", "exec langflow run --host 0.0.0.0 --port ${PORT:-7860} --no-open-browser"]
