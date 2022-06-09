FROM python:3.9-slim-buster

WORKDIR /app
RUN addgroup --system appuser && adduser --system --group appuser && chown -R appuser:appuser /app/

RUN apt-get update -y && apt-get install -y build-essential
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -U setuptools pip && pip install --no-cache-dir -r requirements.txt

COPY ./src/ /app
USER appuser
CMD ["pytest"]
