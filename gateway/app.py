import os
import requests
from flask import Flask, request, jsonify
import grpc
import posts_pb2, posts_pb2_grpc
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5000")
POSTS_SERVICE_URL = os.getenv("POSTS_SERVICE_URL", "posts-service:50051")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-key")

channel = grpc.insecure_channel(POSTS_SERVICE_URL)
post_stub = posts_pb2_grpc.PostServiceStub(channel)


jwt = JWTManager(app)
def get_user_id_from_jwt():
    try:
        return int(get_jwt_identity())
    except Exception as e:
        print(f"Error extracting user ID from JWT: {e}")
        return None

@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    response = requests.post(f"{USER_SERVICE_URL}/register", json=data)
    return jsonify(response.json()), response.status_code

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = requests.post(f"{USER_SERVICE_URL}/login", json=data)
    return jsonify(response.json()), response.status_code

@app.route('/users/myprofile', methods=['GET'])
def get_profile():
    response = requests.get(f"{USER_SERVICE_URL}/users/profile", headers=request.headers)
    return jsonify(response.json()), response.status_code

@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    response = requests.get(f"{USER_SERVICE_URL}/users/{username}")
    return jsonify(response.json()), response.status_code

@app.route('/users/update_profile', methods=['PUT'])
def update_user_profile():
    data = request.get_json()
    response = requests.put(f"{USER_SERVICE_URL}/users/update_profile", json=data, headers=request.headers)
    return jsonify(response.json()), response.status_code


@app.route('/posts/create', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    creator_id = get_user_id_from_jwt()
    if not creator_id:
        return jsonify({"error": "Unauthorized"}), 401
    title = data.get("title")
    if not title:
        return jsonify({"error": "Title is required"}), 400


    grpc_request = posts_pb2.CreatePostRequest(
        title=data.get("title"),
        description=data.get("description"),
        creator_id=creator_id,
        is_private=data.get("is_private", False),
        tags=data.get("tags", [])
    )

    try:
        grpc_response = post_stub.CreatePost(grpc_request)
        return jsonify({
            "id": grpc_response.id,
            "title": grpc_response.title,
            "description": grpc_response.description,
            "creator_id": grpc_response.creator_id,
            "created_date": grpc_response.created_date,
            "updated_date": grpc_response.updated_date,
            "is_private": grpc_response.is_private,
            "tags": list(grpc_response.tags)
        }), 201
    except grpc.RpcError as e:
        return jsonify({"error": str(e.details())}), 500


@app.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    creator_id = get_user_id_from_jwt()
    if not creator_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        grpc_request = posts_pb2.GetPostRequest(post_id=post_id, creator_id=creator_id)
        grpc_response = post_stub.GetPost(grpc_request)
        return jsonify({
            "id": grpc_response.id,
            "title": grpc_response.title,
            "description": grpc_response.description,
            "creator_id": grpc_response.creator_id,
            "created_date": grpc_response.created_date,
            "updated_date": grpc_response.updated_date,
            "is_private": grpc_response.is_private,
            "tags": list(grpc_response.tags)
        }), 200
    except grpc.RpcError as e:
        return jsonify({"error": str(e.details())}), 500


@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    data = request.get_json()
    creator_id = get_user_id_from_jwt()
    if not creator_id:
        return jsonify({"error": "Unauthorized"}), 401

    grpc_request = posts_pb2.UpdatePostRequest(
        id=post_id,
        title=data.get("title"),
        description=data.get("description"),
        creator_id=creator_id,
        is_private=data.get("is_private", False),
        tags=data.get("tags", [])
    )

    try:
        grpc_response = post_stub.UpdatePost(grpc_request)
        return jsonify({
            "id": grpc_response.id,
            "title": grpc_response.title,
            "description": grpc_response.description,
            "creator_id": grpc_response.creator_id,
            "created_date": grpc_response.created_date,
            "updated_date": grpc_response.updated_date,
            "is_private": grpc_response.is_private,
            "tags": list(grpc_response.tags)
        }), 200
    except grpc.RpcError as e:
        return jsonify({"error": str(e.details())}), 500


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    creator_id = get_user_id_from_jwt()
    if not creator_id:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        grpc_request = posts_pb2.DeletePostRequest(post_id=post_id, creator_id=creator_id)
        post_stub.DeletePost(grpc_request)
        return jsonify({"message": "Post deleted successfully"}), 200
    except grpc.RpcError as e:
        return jsonify({"error": str(e.details())}), 500


@app.route('/posts/list', methods=['GET'])
@jwt_required()
def list_posts():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    creator_id = get_user_id_from_jwt()

    grpc_request = posts_pb2.GetListOfPostsRequest(
        page=page,
        page_size=page_size,
        creator_id=creator_id
    )

    try:
        grpc_response = post_stub.GetListOfPosts(grpc_request)
        posts_list = [{
            "id": post.id,
            "title": post.title,
            "description": post.description,
            "creator_id": post.creator_id,
            "created_date": post.created_date,
            "updated_date": post.updated_date,
            "is_private": post.is_private,
            "tags": list(post.tags)
        } for post in grpc_response.posts]

        return jsonify(posts_list), 200
    except grpc.RpcError as e:
        return jsonify({"error": str(e.details())}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
