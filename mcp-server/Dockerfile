FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MOCK_API_URL=http://ariba-mock:8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# MCP server runs via stdio
CMD ["python", "server.py"]
