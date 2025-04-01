import grpc
from concurrent import futures
from datetime import datetime, timezone
from flask import Flask
import os
from database_post import db, Post
import posts_pb2, posts_pb2_grpc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'POSTS_DATABASE_URL',
    'postgresql://student:verystrongpassword@posts_db:5432/posts_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


class PostServicer(posts_pb2_grpc.PostServiceServicer):
    def CreatePost(self, request, context):
        with app.app_context():
            new_post = Post(
                title=request.title,
                description=request.description,
                creator_id=request.creator_id,
                is_private=request.is_private,
                tags=request.tags
            )
            db.session.add(new_post)
            db.session.commit()

            return posts_pb2.Post(
                id=new_post.id,
                title=new_post.title,
                description=new_post.description,
                creator_id=new_post.creator_id,
                created_date=new_post.created_date.isoformat(),
                updated_date=new_post.updated_date.isoformat(),
                is_private=new_post.is_private,
                tags=new_post.tags
            )

    def GetPost(self, request, context):
        with app.app_context():
            post = Post.query.filter_by(id=request.post_id).first()
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

            if post.is_private and post.creator_id != request.creator_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")

            return posts_pb2.Post(
                id=post.id,
                title=post.title,
                description=post.description,
                creator_id=post.creator_id,
                created_date=post.created_date.isoformat(),
                updated_date=post.updated_date.isoformat(),
                is_private=post.is_private,
                tags=post.tags
            )

    def UpdatePost(self, request, context):
        with app.app_context():
            post = Post.query.filter_by(id=request.id).first()
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

            if post.creator_id != request.creator_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")

            post.title = request.title
            post.description = request.description
            post.is_private = request.is_private
            post.tags = request.tags
            post.updated_date = datetime.now(timezone.utc)

            db.session.commit()

            return posts_pb2.Post(
                id=post.id,
                title=post.title,
                description=post.description,
                creator_id=post.creator_id,
                created_date=post.created_date.isoformat(),
                updated_date=post.updated_date.isoformat(),
                is_private=post.is_private,
                tags=post.tags
            )

    def DeletePost(self, request, context):
        with app.app_context():
            post = Post.query.filter_by(id=request.post_id).first()
            if not post:
                context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

            if post.creator_id != request.creator_id:
                context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")

            db.session.delete(post)
            db.session.commit()
            return posts_pb2.Empty()

    def GetListOfPosts(self, request, context):
        with app.app_context():
            query = Post.query

            if request.creator_id:
                query = query.filter((Post.creator_id == request.creator_id) | (Post.is_private == False))

            posts = query.paginate(page=request.page, per_page=request.page_size, error_out=False)

            response = posts_pb2.GetListOfPostsResponse()
            for post in posts.items:
                response.posts.append(posts_pb2.Post(
                    id=post.id,
                    title=post.title,
                    description=post.description,
                    creator_id=post.creator_id,
                    created_date=post.created_date.isoformat(),
                    updated_date=post.updated_date.isoformat(),
                    is_private=post.is_private,
                    tags=post.tags
                ))

            return response


def start():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    posts_pb2_grpc.add_PostServiceServicer_to_server(PostServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    start()
