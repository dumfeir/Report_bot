FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
