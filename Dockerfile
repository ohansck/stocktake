FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -r app/requirements.txt

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["gunicorn", "--chdir", "app", "-b", "127.0.0.1:5000", "-w", "2", "main:app"]
