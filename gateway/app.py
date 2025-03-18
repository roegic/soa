import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:5000")

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

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=4000)
