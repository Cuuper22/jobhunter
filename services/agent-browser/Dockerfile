FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

# Copy and install dependencies
COPY services/agent-browser/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright Chromium
RUN playwright install chromium

# Copy shared code
COPY services/shared/ /app/shared/

# Copy service code
COPY services/agent-browser/ /app/agent_browser/

# Copy context docs
RUN mkdir -p /app/context

ENV PORT=8080
ENV CONTEXT_DIR=/app/context
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "agent_browser.main:app", "--host", "0.0.0.0", "--port", "8080"]
