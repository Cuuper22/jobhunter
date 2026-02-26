FROM python:3.12-slim

WORKDIR /app

COPY services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared code
COPY services/shared/ /app/shared/

# Copy service code
COPY services/api-gateway/ /app/api_gateway/

ENV PORT=8080
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8080"]
