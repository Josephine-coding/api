# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster
WORKDIR /api
COPY . .
RUN pip3 install -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
