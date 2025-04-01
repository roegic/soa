FROM python:3.10

WORKDIR /app

COPY ./tests/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./users_service /app/users_service
COPY ./gateway /app/gateway
COPY ./tests /app/tests
COPY ./proto ./proto
COPY ./posts_service /app/posts_service

ENV PYTHONPATH=/app/users_service:/app/gateway:/app/posts_service:/app/tests:/app


WORKDIR /app/gateway
RUN python -m grpc_tools.protoc -I/app/proto --python_out=. --grpc_python_out=. /app/proto/posts.proto

WORKDIR /app/tests
CMD ["pytest", "-v"]
