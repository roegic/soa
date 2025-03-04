import pytest
from unittest.mock import patch
from gateway.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('gateway.app.requests.post')
def test_register_user(mock_post, client):
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"message": "User registered successfully"}

    response = client.post('/register', json={
        'username': 'mike_wazowski',
        'password': 'strongpassword',
        'email': 'mike.wazowski@example.com'
    })

    assert response.status_code == 201
    assert response.get_json()['message'] == "User registered successfully"

@patch('gateway.app.requests.post')
def test_login_user(mock_post, client):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "fake-jwt-token"}

    response = client.post('/login', json={
        'username': 'mike_wazowski',
        'password': 'strongpassword'
    })

    assert response.status_code == 200
    assert 'access_token' in response.get_json()

@patch('gateway.app.requests.get')
def test_get_profile(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "username": "mike_wazowski",
        "first_name": "Mike",
        "last_name": "Wazowski"
    }

    response = client.get('/users/myprofile', headers={
        'Authorization': 'Bearer fake-jwt-token'
    })

    assert response.status_code == 200
    assert response.get_json()['username'] == 'mike_wazowski'
    assert response.get_json()['first_name'] == 'Mike'
    assert response.get_json()['last_name'] == 'Wazowski'

@patch('gateway.app.requests.get')
def test_get_user_by_username(mock_get, client):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "username": "mike_wazowski",
        "first_name": "Mike",
        "last_name": "Wazowski"
    }

    response = client.get('/users/mike_wazowski')

    assert response.status_code == 200
    assert response.get_json()['username'] == 'mike_wazowski'
    assert response.get_json()['first_name'] == 'Mike'
    assert response.get_json()['last_name'] == 'Wazowski'
