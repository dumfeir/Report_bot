FROM python:3.9-slim

WORKDIR /app

# تثبيت المتطلبات النظامية لـ pycairo
RUN apt-get update && \
    apt-get install -y \
    libcairo2-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
