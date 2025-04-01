from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000))
    creator_id = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_date = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    is_private = db.Column(db.Boolean, default=False)
    tags = db.Column(db.ARRAY(db.String(255)))