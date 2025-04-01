import pytest
from unittest.mock import patch, MagicMock
from flask_jwt_extended import create_access_token

from gateway.app import app, posts_pb2, posts_pb2_grpc

TEST_USER_ID = 1
TEST_JWT_SECRET = "super-secret-key"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = TEST_JWT_SECRET
    with app.app_context():
        yield app.test_client()


@pytest.fixture
def auth_headers():
    with app.app_context():
        access_token = create_access_token(identity=str(TEST_USER_ID))
    return {"Authorization": f"Bearer {access_token}"}


def create_mock_post(**kwargs):
    mock_post = MagicMock(spec=posts_pb2.Post)
    mock_post.id = kwargs.get("id", 1)
    mock_post.title = kwargs.get("title", "Test Post")
    mock_post.description = kwargs.get("description", "Test Description")
    mock_post.creator_id = kwargs.get("creator_id", TEST_USER_ID)
    mock_post.is_private = kwargs.get("is_private", False)
    mock_post.created_date = kwargs.get("created_date", "1984-01-01T00:00:00Z")
    mock_post.updated_date = kwargs.get("updated_date", "1984-01-01T00:00:00Z")
    mock_post.tags = kwargs.get("tags", ["test", "mock"])
    return mock_post


def test_create_post_unauthorized(client):
    response = client.post("/posts/create", json={"title": "Test"})
    assert response.status_code == 401
    assert "Authorization" in response.json.get("msg", "")


@patch("gateway.app.post_stub")
def test_create_post_success(mock_post_stub, client, auth_headers):
    mock_response = create_mock_post(title="New Post", tags=["grpc", "test"])
    mock_post_stub.CreatePost.return_value = mock_response

    post_data = {
        "title": "New Post",
        "description": "Some description",
        "is_private": False,
        "tags": ["grpc", "test"],
    }
    response = client.post("/posts/create", json=post_data, headers=auth_headers)

    assert response.status_code == 201
    assert response.json["title"] == "New Post"
    mock_post_stub.CreatePost.assert_called_once()


@patch("gateway.app.post_stub")
def test_get_post_success(mock_post_stub, client, auth_headers):
    post_id = 42
    mock_response = create_mock_post(id=post_id, title="Sample Post")
    mock_post_stub.GetPost.return_value = mock_response

    response = client.get(f"/posts/{post_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json["id"] == post_id
    mock_post_stub.GetPost.assert_called_once()


@patch("gateway.app.post_stub")
def test_update_post_success(mock_post_stub, client, auth_headers):
    post_id = 99
    updated_data = {"title": "Updated", "description": "Updated Content", "tags": ["edit"]}
    mock_response = create_mock_post(id=post_id, **updated_data)

    mock_post_stub.UpdatePost.return_value = mock_response

    response = client.put(f"/posts/{post_id}", json=updated_data, headers=auth_headers)

    assert response.status_code == 200
    assert response.json["title"] == "Updated"
    mock_post_stub.UpdatePost.assert_called_once()


@patch("gateway.app.post_stub")
def test_delete_post_success(mock_post_stub, client, auth_headers):
    post_id = 55
    mock_post_stub.DeletePost.return_value = MagicMock()

    response = client.delete(f"/posts/{post_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json["message"] == "Post deleted successfully"
    mock_post_stub.DeletePost.assert_called_once()


@patch("gateway.app.post_stub")
def test_list_posts_success(mock_post_stub, client, auth_headers):
    mock_post1 = create_mock_post(id=1, title="First Post")
    mock_post2 = create_mock_post(id=2, title="Second Post")

    mock_response = MagicMock(spec=posts_pb2.GetListOfPostsResponse)
    mock_response.posts = [mock_post1, mock_post2]
    mock_post_stub.GetListOfPosts.return_value = mock_response

    response = client.get("/posts/list?page=1&page_size=10", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json) == 2
    mock_post_stub.GetListOfPosts.assert_called_once()
