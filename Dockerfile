FROM python:3.13.3

WORKDIR /app

COPY src/ ./src/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]