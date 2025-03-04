import pytest
from users_service.app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.close()
            db.drop_all()

@pytest.fixture
def auth_header(client):
    register_data = {
        "username": "testuser",
        "password": "testpassword",
        "email": "test@example.com"
    }
    client.post('/register', json=register_data)
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    login_response = client.post('/login', json=login_data)
    access_token = login_response.get_json()['access_token']
    return {'Authorization': f'Bearer {access_token}'}


def test_register_success(client):
    response = client.post('/register', json={
        'username': 'newuser',
        'password': 'newpassword123',
        'email': 'newuser@example.com'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_register_duplicate_username(client):
    client.post('/register', json={'username': 'existinguser', 'password': 'password123', 'email': 'exist@example.com'})
    response = client.post('/register', json={'username': 'existinguser', 'password': 'anotherpassword123', 'email': 'another@example.com'})
    assert response.status_code == 400
    assert response.json['message'] == 'Oops, user with this username already exists!'

def test_login_success(client):
    client.post('/register', json={'username': 'loginuser', 'password': 'loginpassword123', 'email': 'login@example.com'})
    response = client.post('/login', json={
        'username': 'loginuser',
        'password': 'loginpassword123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/login', json={
        'username': 'loginuser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid username or password'

def test_login_validation_error_missing_username(client):
    response = client.post('/login', json={
        'password': 'password123'
    })
    assert response.status_code == 400
    assert "Request error" in response.json['error']
    assert "'username' is a required property" in response.json['error']


def test_login_validation_error_missing_password(client):
    response = client.post('/login', json={
        'username': 'loginuser'
    })
    assert response.status_code == 400
    assert "Request error" in response.json['error']
    assert "'password' is a required property" in response.json['error']

def test_get_profile_success(client, auth_header):
    response = client.get('/users/profile', headers=auth_header)
    assert response.status_code == 200
    assert response.json['username'] == 'testuser'
    assert response.json['email'] == 'test@example.com'

def test_get_profile_unauthorized(client):
    response = client.get('/users/profile')
    assert response.status_code == 401

def test_update_profile_success(client, auth_header):
    update_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "email": "updated_email@example.com",
        "phone_number": "9876543210",
        "birthday": "10-10-2000"
    }
    response = client.put('/users/update_profile', json=update_data, headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'User data updated successfully!'

def test_update_profile_unauthorized(client):
    update_data = {
        "first_name": "UpdatedFirstName",
        "last_name": "UpdatedLastName",
        "email": "updated_email@example.com",
        "phone_number": "9876543210",
        "birthday": "10-10-2000"
    }
    response = client.put('/users/update_profile', json=update_data)
    assert response.status_code == 401


def test_update_profile_invalid_birthday_format(client, auth_header):
    update_data = {
        "birthday": "10-1984-10"
    }
    response = client.put('/users/update_profile', json=update_data, headers=auth_header)
    assert response.status_code == 400
    assert "Invalid birthday date format. Required format is" in response.json['message']
