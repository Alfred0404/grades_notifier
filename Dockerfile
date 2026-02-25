FROM node:20-alpine AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build:docker

FROM python:3.12-alpine

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    libstdc++ \
    build-base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY start.sh ./start.sh
COPY .env.example ./.env.example
COPY --from=frontend-builder /build/frontend/dist ./src/web/static

RUN chmod +x ./start.sh

EXPOSE 8000
CMD ["./start.sh"]
