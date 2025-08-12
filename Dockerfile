FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m -u 1000 appuser
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser main.py .

USER appuser

EXPOSE 8000

# uvicorn 엔트리 (개발모드면 --reload를 compose에서 덮어쓰기 권장)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
