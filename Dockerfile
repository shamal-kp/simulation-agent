FROM python:3.11-slim

WORKDIR /app

COPY ./ .

RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    else \
        echo "No requirements.txt found"; \
    fi

# https://github.com/azure/azure-sdk-for-python/issues/44884
RUN python patches/fix_otel_streaming.py

EXPOSE 8088

CMD ["python", "main.py"]
