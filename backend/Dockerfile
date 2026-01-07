# Dockerfile dla Kalkulator Podatkowy JDG
# Python 3.12 backend

FROM python:3.12-slim

# Metadata
LABEL maintainer="Kalkulator Podatkowy JDG"
LABEL description="Backend API dla kalkulatora podatkowego JDG (2025)"

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki zależności
COPY requirements.txt .
COPY pyproject.toml .

# Zainstaluj zależności
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY app/ ./app/
COPY main.py .

# Eksponuj port
EXPOSE 8000

# Zdrowie kontenera
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Uruchom aplikację
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
