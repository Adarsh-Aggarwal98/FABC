"""
Import Log model for tracking import operations.
"""
from datetime import datetime
from app.extensions import db


class ImportLog(db.Model):
    """Model for tracking CSV/Excel import operations"""
    __tablename__ = 'import_logs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String(36), db.ForeignKey('companies.id'), nullable=True)
    imported_by_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    import_type = db.Column(db.String(50), nullable=False)  # 'users', 'clients', 'services', etc.
    filename = db.Column(db.String(255), nullable=True)
    total_rows = db.Column(db.Integer, default=0)
    imported_count = db.Column(db.Integer, default=0)
    skipped_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    errors = db.Column(db.JSON, nullable=True)  # Store error details as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref=db.backref('import_logs', lazy='dynamic'))
    imported_by = db.relationship('User', backref=db.backref('import_logs', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'imported_by_id': self.imported_by_id,
            'import_type': self.import_type,
            'filename': self.filename,
            'total_rows': self.total_rows,
            'imported_count': self.imported_count,
            'skipped_count': self.skipped_count,
            'error_count': self.error_count,
            'errors': self.errors,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<ImportLog {self.id} - {self.import_type}>'
