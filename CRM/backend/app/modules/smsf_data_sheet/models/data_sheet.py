"""SMSFDataSheet Model — stores SMSF Basic Data Sheet per fund and financial year"""
from datetime import datetime
from app.extensions import db


class SMSFDataSheet(db.Model):
    """
    Stores a completed SMSF Basic Data Sheet for a specific fund (ClientEntity)
    and financial year.  All repeating sections (members, trustees, nominations,
    subsequent events) are stored as JSON arrays so the structure stays flexible.
    """
    __tablename__ = 'smsf_data_sheets'

    id = db.Column(db.Integer, primary_key=True)

    # Linked fund
    client_entity_id = db.Column(
        db.String(36),
        db.ForeignKey('client_entities.id', ondelete='CASCADE'),
        nullable=False
    )

    # Financial year this sheet covers (e.g. "2025" → FY ending 30/06/2025)
    financial_year = db.Column(db.String(20), nullable=False)

    # ── Section 1: Fund Details ──────────────────────────────────────────────
    fund_name        = db.Column(db.String(300))
    date_of_creation = db.Column(db.String(50))
    abn_of_smsf      = db.Column(db.String(30))
    tfn_of_smsf      = db.Column(db.String(30))

    # ── Section 2: Members (up to 4) ────────────────────────────────────────
    # Each entry: {name, address, dob, tfn, date_of_joining}
    members = db.Column(db.JSON, default=list)

    # ── Section 3: Trustees (up to 4) ───────────────────────────────────────
    # Each entry: {name, address, acn}
    trustees = db.Column(db.JSON, default=list)

    # ── Section 4: Bare Trustee Details ─────────────────────────────────────
    # {bare_trust_name, bare_trustee_name, address, acn}
    bare_trustee = db.Column(db.JSON, default=dict)

    # ── Section 5: Nomination Details ───────────────────────────────────────
    # List of 4 items (one per member), each item is a list of {nominee, relation, percentage}
    nominations = db.Column(db.JSON, default=list)

    # ── Section 6: Subsequent Events ────────────────────────────────────────
    # Each entry: {date, name_of_event}
    subsequent_events = db.Column(db.JSON, default=list)

    # Audit trail
    created_by_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client_entity = db.relationship('ClientEntity', backref=db.backref('smsf_data_sheets', lazy='dynamic'))
    created_by    = db.relationship('User', foreign_keys=[created_by_id])

    def to_dict(self):
        return {
            'id':               self.id,
            'client_entity_id': self.client_entity_id,
            'client_entity_name': self.client_entity.name if self.client_entity else None,
            'financial_year':   self.financial_year,
            'fund_name':        self.fund_name,
            'date_of_creation': self.date_of_creation,
            'abn_of_smsf':      self.abn_of_smsf,
            'tfn_of_smsf':      self.tfn_of_smsf,
            'members':          self.members or [],
            'trustees':         self.trustees or [],
            'bare_trustee':     self.bare_trustee or {},
            'nominations':      self.nominations or [],
            'subsequent_events':self.subsequent_events or [],
            'created_by_id':    self.created_by_id,
            'created_at':       self.created_at.isoformat() if self.created_at else None,
            'updated_at':       self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<SMSFDataSheet FY{self.financial_year} entity={self.client_entity_id}>'
