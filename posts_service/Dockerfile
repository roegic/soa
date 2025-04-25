FROM python:3.10

WORKDIR /app

COPY posts_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./posts_service ./posts_service
COPY ./proto ./proto

WORKDIR /app/posts_service

RUN python -m grpc_tools.protoc -I/app/proto --python_out=. --grpc_python_out=. /app/proto/posts.proto

CMD ["python", "app.py"]