FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY pfactor.py .
COPY adk_agent.py .
COPY seed_data.py .
COPY new_endpoints.py .
COPY monitor.py .
COPY upload_endpoint.py .
COPY memory/ ./memory/

RUN mkdir -p uploads tts_output

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
