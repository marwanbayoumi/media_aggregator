FROM python:3.11-slim

COPY static/ templates/ app.py requirements.txt /app/

RUN pip --no-cache-dir install -r /app/requirements.txt

RUN pip install gunicorn

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]