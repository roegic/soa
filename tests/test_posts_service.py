import pytest
import grpc
from unittest.mock import patch, MagicMock
import posts_pb2
import posts_pb2_grpc
from posts_service.app import PostServicer, app, db, Post


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def grpc_stub():
    return posts_pb2_grpc.PostServiceStub(grpc.insecure_channel("localhost:50051"))


@pytest.fixture
def servicer():
    return PostServicer()

def test_create_post(client, servicer):
    request = posts_pb2.CreatePostRequest(
        title="Test Post",
        description="Description of test post",
        creator_id=1,
        is_private=False,
        tags=["test", "grpc"]
    )
    response = servicer.CreatePost(request, None)
    assert response.id is not None
    assert response.title == "Test Post"

def test_get_post(client, servicer):
    with app.app_context():
        post = Post(title="Sample", description="Test", creator_id=1, is_private=False, tags=["sample"])
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    with app.app_context():
        request = posts_pb2.GetPostRequest(post_id=post_id, creator_id=1)
        response = servicer.GetPost(request, MagicMock())
        assert response.id == post_id
        assert response.title == "Sample"

def test_update_post(client, servicer):
    with app.app_context():
        post = Post(title="Old Title", description="Old Desc", creator_id=1, is_private=False, tags=["old"])
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    with app.app_context():
        request = posts_pb2.UpdatePostRequest(
            id=post_id, title="New Title", description="New Desc", creator_id=1, is_private=True, tags=["new"]
        )
        response = servicer.UpdatePost(request, MagicMock())
        assert response.title == "New Title"

def test_delete_post(client, servicer):
    with app.app_context():
        post = Post(title="To Delete", description="Delete me", creator_id=1, is_private=False, tags=["delete"])
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    with app.app_context():
        request = posts_pb2.DeletePostRequest(post_id=post_id, creator_id=1)
        response = servicer.DeletePost(request, MagicMock())
        assert response is not None

    with app.app_context():
        assert db.session.get(Post, post_id) is None

