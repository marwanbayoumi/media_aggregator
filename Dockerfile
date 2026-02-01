FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \ sqlite3 \ libsqlite3-dev \ && rm -rf /var/lib/apt/lists/*

COPY app/ /app/

WORKDIR /app

RUN pip --no-cache-dir install -r /app/requirements.txt

RUN pip install gunicorn

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]