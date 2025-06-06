FROM python:3.13.3-slim-bullseye

# Pour éviter les warnings et accélérer pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

COPY src/ ./src/

CMD ["python", "src/main.py"]