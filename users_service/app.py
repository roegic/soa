import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from database import db, User
import yaml
from jsonschema import validate, ValidationError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/mydb")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "my-super-duper-secret-key")

db.init_app(app)
jwt = JWTManager(app)
openapi_file_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
with open(openapi_file_path, "r") as f:
    openapi_spec = yaml.safe_load(f)

def validate_request(schema_name, data):
    try:
        schema = openapi_spec['components']['schemas'][schema_name]
        validate(instance=data, schema=schema)
        return True, None
    except (KeyError, ValidationError) as e:
        return False, str(e).splitlines()[0]

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    is_valid, error_message = validate_request("UserRegisterRequest", data)
    if not is_valid:
        return jsonify({"error": f"Request error: {error_message}"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Oops, user with this username already exists!"}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password, email=email)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    is_valid, error_message = validate_request("UserLoginRequest", data)
    if not is_valid:
        return jsonify({"error": f"Request error: {error_message}"}), 400

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.hashed_password, password):
        return jsonify({"message": "Invalid username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200

@app.route("/users/profile", methods=["GET"])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"message": f"User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "birthday": user.birthday,
        "created_time": user.created_time,
        "updated_time": user.updated_time
    }), 200


@app.route("/users/<username>", methods=["GET"])
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User not found!"}), 404

    return jsonify({
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "birthday": user.birthday
    }), 200

@app.route("/users/update_profile", methods=["PUT"])
@jwt_required()
def update_user():
    current_user = get_jwt_identity()
    data = request.get_json()
    user = User.query.filter_by(username=current_user).first()

    is_valid, error_message = validate_request("UserProfileUpdateRequest", data)
    if not is_valid:
        return jsonify({"error": f"Request error: {error_message}"}), 400

    if not user:
        return jsonify({"message": f"User not found!"}), 404

    try:
        if data.get("email") is not None:
            user.email = data.get("email", user.email)
        if data.get("first_name") is not None:
            user.first_name = data.get("first_name", user.first_name)
        if data.get("last_name") is not None:
            user.last_name = data.get("last_name", user.last_name)
        if data.get("phone_number") is not None:
            user.phone_number = data.get("phone_number", user.phone_number)
        if data.get("birthday") is not None:
            try:
                user.birthday = datetime.strptime(data.get("birthday"), "%d-%m-%Y").date()
            except ValueError:
                return jsonify({"message": "Invalid birthday date format. Required format is DD-MM-YYYY"}), 400
        db.session.commit()
        return jsonify({"message": "User data updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Error when updating user: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
