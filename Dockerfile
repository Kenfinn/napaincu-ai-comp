# Sentinel Saham — image untuk Dokploy / Docker.
#   docker build -t sentinel .
#   docker run -p 8000:8000 -v sentinel-data:/data sentinel
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SENTINEL_DATA_DIR=/data \
    TZ=Asia/Taipei

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY valuation ./valuation
COPY data/fixtures ./data/fixtures
COPY eval ./eval

# Data hasil tarikan (watchlist, riwayat pengumuman, jejak audit) hidup di volume ini,
# supaya tidak hilang saat redeploy.
RUN useradd --create-home --uid 10001 sentinel && mkdir -p /data && chown sentinel /data
VOLUME ["/data"]
USER sentinel

EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=5s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/sehat', timeout=4)"

# Satu worker: cache hasil pipeline dan pemantau latar belakang hidup di proses ini.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
