FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MOCK_API_URL=http://ariba-mock:8080 \
    RISK_API_URL=http://risk-service:8081

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8082

# MCP server runs via uvicorn (HTTP/SSE + REST API)
CMD ["python", "server.py"]
