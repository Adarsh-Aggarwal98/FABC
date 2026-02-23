"""Blog model — public-facing articles for the AusSuperSource website."""
import uuid
from datetime import datetime
from app.extensions import db


class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    excerpt = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    read_time = db.Column(db.String(50), default='5 min read')
    image = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'content': self.content,
            'category': self.category,
            'author': self.author,
            'readTime': self.read_time,
            'image': self.image,
            'featured': self.featured,
            'published': self.published,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<Blog {self.slug}>'
