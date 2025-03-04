FROM python:3.10

WORKDIR /app

COPY ./tests/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./users_service /app/users_service
COPY ./gateway /app/gateway
COPY ./tests /app/tests

ENV PYTHONPATH=/app/users_service:/app/gateway:/app/tests:/app

WORKDIR /app/tests

CMD ["pytest", "-v"]
