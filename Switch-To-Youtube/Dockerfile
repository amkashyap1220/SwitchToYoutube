FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

ENV PYTHONUNBUFFERED=1 DATA_FOLDER=/data
EXPOSE 8888
CMD ["python", "-m", "app.main"]
