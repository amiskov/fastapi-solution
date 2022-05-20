FROM python:3.9-slim-buster
ENV PORT 8000
EXPOSE ${PORT}/tcp
WORKDIR /app
RUN addgroup --system appuser && adduser --system --group appuser

RUN apt-get update -y && apt-get install -y build-essential
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -U setuptools pip && pip install --no-cache-dir -r requirements.txt

COPY ./src /app
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

USER appuser

CMD ["/app/entrypoint.sh"]
