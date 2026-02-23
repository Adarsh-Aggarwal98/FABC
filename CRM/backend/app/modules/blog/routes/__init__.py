"""
Blog API Routes
===============
Public:  GET  /api/blogs              — list published blogs
Public:  GET  /api/blogs/:slug        — get single blog by slug
Admin:   GET  /api/admin/blogs        — list all blogs (incl. drafts)
Admin:   POST /api/admin/blogs        — create blog
Admin:   PUT  /api/admin/blogs/:id    — update blog
Admin:   DELETE /api/admin/blogs/:id  — delete blog
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from app.extensions import db

blog_bp = Blueprint('blog', __name__)


def _admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            from app.modules.user.models import User
            user = User.query.get(get_jwt_identity())
            if not user or user.role.name not in ('super_admin', 'admin'):
                return jsonify({'success': False, 'error': 'Admin access required'}), 403
        except Exception:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return fn(*args, **kwargs)
    return wrapper


# ── Public routes ─────────────────────────────────────────────────────────────

@blog_bp.route('/api/blogs', methods=['GET'])
def list_blogs():
    """List published blogs. Optional ?featured=true, ?category=X, ?limit=N"""
    from app.modules.blog.models import Blog
    q = Blog.query.filter_by(published=True)
    if request.args.get('featured') == 'true':
        q = q.filter_by(featured=True)
    if request.args.get('category'):
        q = q.filter_by(category=request.args['category'])
    limit = request.args.get('limit', type=int)
    q = q.order_by(Blog.created_at.desc())
    blogs = q.limit(limit).all() if limit else q.all()
    return jsonify({'success': True, 'blogs': [b.to_dict() for b in blogs]})


@blog_bp.route('/api/blogs/<slug>', methods=['GET'])
def get_blog(slug):
    from app.modules.blog.models import Blog
    blog = Blog.query.filter_by(slug=slug, published=True).first()
    if not blog:
        return jsonify({'success': False, 'error': 'Blog not found'}), 404
    return jsonify({'success': True, 'blog': blog.to_dict()})


# ── Admin routes ───────────────────────────────────────────────────────────────

@blog_bp.route('/api/admin/blogs', methods=['GET'])
@_admin_required
def admin_list_blogs():
    from app.modules.blog.models import Blog
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    return jsonify({'success': True, 'blogs': [b.to_dict() for b in blogs]})


@blog_bp.route('/api/admin/blogs', methods=['POST'])
@_admin_required
def create_blog():
    from app.modules.blog.models import Blog
    data = request.get_json() or {}
    required = ['title', 'slug', 'excerpt', 'category', 'author']
    if not all(data.get(f) for f in required):
        return jsonify({'success': False, 'error': 'Missing required fields: ' + ', '.join(required)}), 400
    if Blog.query.filter_by(slug=data['slug']).first():
        return jsonify({'success': False, 'error': 'Slug already exists'}), 409

    blog = Blog(
        title=data['title'],
        slug=data['slug'],
        excerpt=data['excerpt'],
        content=data.get('content'),
        category=data['category'],
        author=data['author'],
        read_time=data.get('readTime', '5 min read'),
        image=data.get('image'),
        featured=data.get('featured', False),
        published=data.get('published', True),
    )
    db.session.add(blog)
    db.session.commit()
    return jsonify({'success': True, 'blog': blog.to_dict()}), 201


@blog_bp.route('/api/admin/blogs/<blog_id>', methods=['PUT', 'PATCH'])
@_admin_required
def update_blog(blog_id):
    from app.modules.blog.models import Blog
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'success': False, 'error': 'Blog not found'}), 404
    data = request.get_json() or {}
    if data.get('slug') and data['slug'] != blog.slug:
        if Blog.query.filter_by(slug=data['slug']).first():
            return jsonify({'success': False, 'error': 'Slug already exists'}), 409
    for field in ['title', 'slug', 'excerpt', 'content', 'category', 'author', 'image']:
        if field in data:
            setattr(blog, field, data[field])
    if 'readTime' in data:
        blog.read_time = data['readTime']
    if 'featured' in data:
        blog.featured = data['featured']
    if 'published' in data:
        blog.published = data['published']
    db.session.commit()
    return jsonify({'success': True, 'blog': blog.to_dict()})


@blog_bp.route('/api/admin/blogs/<blog_id>', methods=['DELETE'])
@_admin_required
def delete_blog(blog_id):
    from app.modules.blog.models import Blog
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'success': False, 'error': 'Blog not found'}), 404
    db.session.delete(blog)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Blog deleted'})
