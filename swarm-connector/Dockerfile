FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY app.py /app/app.py

EXPOSE 5080

CMD ["python3", "/app/app.py"]
