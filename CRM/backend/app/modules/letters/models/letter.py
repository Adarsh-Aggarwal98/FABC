"""AuditLetter Model - Engagement and Representation letters for SMSF audits"""
from datetime import datetime
from app.extensions import db


class AuditLetter(db.Model):
    """
    Represents an Engagement Letter or Trustee Representation Letter
    generated for a specific SMSF client entity and financial year.
    """
    __tablename__ = 'audit_letters'

    LETTER_TYPE_ENGAGEMENT = 'engagement'
    LETTER_TYPE_REPRESENTATION = 'representation'
    VALID_LETTER_TYPES = [LETTER_TYPE_ENGAGEMENT, LETTER_TYPE_REPRESENTATION]

    STATUS_DRAFT = 'draft'
    STATUS_SENT = 'sent'
    STATUS_SIGNED = 'signed'
    VALID_STATUSES = [STATUS_DRAFT, STATUS_SENT, STATUS_SIGNED]

    id = db.Column(db.Integer, primary_key=True)

    # Client entity (SMSF fund)
    client_entity_id = db.Column(
        db.String(36),
        db.ForeignKey('client_entities.id', ondelete='CASCADE'),
        nullable=False
    )

    # Letter metadata
    letter_type = db.Column(db.String(20), nullable=False, default=LETTER_TYPE_ENGAGEMENT)
    financial_year = db.Column(db.String(20), nullable=False)   # e.g. "2025" (01/07/2024 - 30/06/2025)
    letter_date = db.Column(db.String(50))                       # Display date on letter
    status = db.Column(db.String(20), nullable=False, default=STATUS_DRAFT)

    # Auditor details (override company defaults if needed)
    auditor_name = db.Column(db.String(200))
    auditor_registration = db.Column(db.String(100))
    auditor_address = db.Column(db.Text)

    # Trustees JSON: list of {name, company, role, signature_b64, signed_date}
    trustees_data = db.Column(db.JSON, default=list)

    # PDF storage
    # Either the path to a WeasyPrint-generated PDF or an uploaded signed PDF
    pdf_path = db.Column(db.String(500))
    signed_pdf_path = db.Column(db.String(500))

    # Audit trail
    created_by_id = db.Column(
        db.String(36),
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client_entity = db.relationship('ClientEntity', backref=db.backref('audit_letters', lazy='dynamic'))
    created_by = db.relationship('User', foreign_keys=[created_by_id])

    def to_dict(self):
        return {
            'id': self.id,
            'client_entity_id': self.client_entity_id,
            'client_entity_name': self.client_entity.name if self.client_entity else None,
            'letter_type': self.letter_type,
            'financial_year': self.financial_year,
            'letter_date': self.letter_date,
            'status': self.status,
            'auditor_name': self.auditor_name,
            'auditor_registration': self.auditor_registration,
            'auditor_address': self.auditor_address,
            'trustees_data': self.trustees_data or [],
            'has_pdf': bool(self.pdf_path),
            'has_signed_pdf': bool(self.signed_pdf_path),
            'created_by_id': self.created_by_id,
            'created_by_name': (
                f"{self.created_by.first_name} {self.created_by.last_name}"
                if self.created_by else None
            ),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<AuditLetter {self.letter_type} FY{self.financial_year} for {self.client_entity_id}>'
