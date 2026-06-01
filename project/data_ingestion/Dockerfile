FROM python:3.12-slim

WORKDIR /app

COPY data_ingestion/requirements.txt ./data_ingestion/requirements.txt
RUN pip install --no-cache-dir -r data_ingestion/requirements.txt

COPY backend/ ./backend/
COPY data_ingestion/ ./data_ingestion/

CMD ["python", "-m", "data_ingestion.run_all"]
