"""
Company Model
=============

Company/Practice model for managing accounting practices.
"""
import uuid
from datetime import datetime
from app.extensions import db


class Company(db.Model):
    """Company/Practice model for managing accounting practices"""
    __tablename__ = 'companies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Company Details
    name = db.Column(db.String(200), nullable=False)
    trading_name = db.Column(db.String(200))  # If different from legal name
    abn = db.Column(db.String(20))  # Australian Business Number
    acn = db.Column(db.String(20))  # Australian Company Number

    # Contact Details
    email = db.Column(db.String(120))  # Company email
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))

    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    postcode = db.Column(db.String(10))
    country = db.Column(db.String(100), default='Australia')

    # Practice Owner (Admin) - Reference to User who is the owner
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    # Subscription/Plan (for future use)
    plan_type = db.Column(db.String(50), default='standard')  # 'starter', 'standard', 'premium'
    max_users = db.Column(db.Integer, default=10)
    max_clients = db.Column(db.Integer, default=100)

    # Status
    is_active = db.Column(db.Boolean, default=True)

    # Company Type
    company_type = db.Column(db.String(50), default='tax_agent')  # tax_agent, auditor, bookkeeper, financial_planner, bas_agent, mortgage_broker, other

    # Company Type Constants
    TYPE_TAX_AGENT = 'tax_agent'
    TYPE_AUDITOR = 'auditor'
    TYPE_BOOKKEEPER = 'bookkeeper'
    TYPE_FINANCIAL_PLANNER = 'financial_planner'
    TYPE_BAS_AGENT = 'bas_agent'
    TYPE_MORTGAGE_BROKER = 'mortgage_broker'
    TYPE_ACCOUNTANT = 'accountant'
    TYPE_OTHER = 'other'

    # Branding (optional)
    logo_url = db.Column(db.String(500))  # Legacy - URL based storage
    logo_data = db.Column(db.LargeBinary)  # Store logo image directly in DB
    logo_mime_type = db.Column(db.String(50))  # e.g., 'image/png', 'image/jpeg'
    primary_color = db.Column(db.String(20), default='#4F46E5')  # Hex color - default indigo
    secondary_color = db.Column(db.String(20), default='#10B981')  # Hex color - default emerald
    tertiary_color = db.Column(db.String(20), default='#6366F1')  # Hex color - default violet

    # Sidebar branding colors
    sidebar_bg_color = db.Column(db.String(20), default='#0f172a')  # Hex color - default slate-900
    sidebar_text_color = db.Column(db.String(20), default='#ffffff')  # Hex color - default white
    sidebar_hover_bg_color = db.Column(db.String(20), default='#334155')  # Hex color - default slate-700

    # Currency and Tax Configuration
    currency = db.Column(db.String(3), default='AUD')  # ISO 4217 currency code
    currency_symbol = db.Column(db.String(5), default='$')  # Currency symbol for display
    tax_type = db.Column(db.String(20), default='GST')  # GST, VAT, Sales Tax, none
    tax_label = db.Column(db.String(20), default='GST')  # Display label for tax
    default_tax_rate = db.Column(db.Numeric(5, 2), default=10.00)  # Default tax percentage

    # Tax type constants
    TAX_GST = 'GST'  # Australia, NZ, Singapore, India
    TAX_VAT = 'VAT'  # UK, EU, Middle East
    TAX_SALES_TAX = 'Sales Tax'  # US
    TAX_NONE = 'none'

    # Comprehensive currency list with symbols and names
    CURRENCIES = {
        # Oceania
        'AUD': {'symbol': '$', 'name': 'Australian Dollar'},
        'NZD': {'symbol': '$', 'name': 'New Zealand Dollar'},
        'FJD': {'symbol': '$', 'name': 'Fiji Dollar'},

        # North America
        'USD': {'symbol': '$', 'name': 'US Dollar'},
        'CAD': {'symbol': '$', 'name': 'Canadian Dollar'},
        'MXN': {'symbol': '$', 'name': 'Mexican Peso'},

        # Europe
        'GBP': {'symbol': '\u00a3', 'name': 'British Pound'},
        'EUR': {'symbol': '\u20ac', 'name': 'Euro'},
        'CHF': {'symbol': 'CHF', 'name': 'Swiss Franc'},

        # Middle East / Gulf Countries
        'AED': {'symbol': '\u062f.\u0625', 'name': 'UAE Dirham'},
        'SAR': {'symbol': '\ufdfc', 'name': 'Saudi Riyal'},
        'QAR': {'symbol': '\u0631.\u0642', 'name': 'Qatari Riyal'},
        'KWD': {'symbol': '\u062f.\u0643', 'name': 'Kuwaiti Dinar'},
        'BHD': {'symbol': '.\u062f.\u0628', 'name': 'Bahraini Dinar'},
        'OMR': {'symbol': '\u0631.\u0639.', 'name': 'Omani Rial'},
        'JOD': {'symbol': '\u062f.\u0627', 'name': 'Jordanian Dinar'},
        'EGP': {'symbol': '\u00a3', 'name': 'Egyptian Pound'},
        'ILS': {'symbol': '\u20aa', 'name': 'Israeli Shekel'},

        # Asia
        'SGD': {'symbol': '$', 'name': 'Singapore Dollar'},
        'HKD': {'symbol': '$', 'name': 'Hong Kong Dollar'},
        'INR': {'symbol': '\u20b9', 'name': 'Indian Rupee'},
        'JPY': {'symbol': '\u00a5', 'name': 'Japanese Yen'},
        'CNY': {'symbol': '\u00a5', 'name': 'Chinese Yuan'},
        'KRW': {'symbol': '\u20a9', 'name': 'South Korean Won'},
        'MYR': {'symbol': 'RM', 'name': 'Malaysian Ringgit'},
        'THB': {'symbol': '\u0e3f', 'name': 'Thai Baht'},
        'PHP': {'symbol': '\u20b1', 'name': 'Philippine Peso'},
        'IDR': {'symbol': 'Rp', 'name': 'Indonesian Rupiah'},
        'VND': {'symbol': '\u20ab', 'name': 'Vietnamese Dong'},
        'PKR': {'symbol': '\u20a8', 'name': 'Pakistani Rupee'},
        'LKR': {'symbol': '\u20a8', 'name': 'Sri Lankan Rupee'},
        'BDT': {'symbol': '\u09f3', 'name': 'Bangladeshi Taka'},

        # Africa
        'ZAR': {'symbol': 'R', 'name': 'South African Rand'},
        'NGN': {'symbol': '\u20a6', 'name': 'Nigerian Naira'},
        'KES': {'symbol': 'KSh', 'name': 'Kenyan Shilling'},

        # South America
        'BRL': {'symbol': 'R$', 'name': 'Brazilian Real'},
        'ARS': {'symbol': '$', 'name': 'Argentine Peso'},
        'CLP': {'symbol': '$', 'name': 'Chilean Peso'},
        'COP': {'symbol': '$', 'name': 'Colombian Peso'},
    }

    # Legacy currency symbol mapping (for backwards compatibility)
    CURRENCY_SYMBOLS = {code: data['symbol'] for code, data in CURRENCIES.items()}

    # Default tax rates by region/currency
    DEFAULT_TAX_RATES = {
        'GST_AU': 10.00,   # Australia GST
        'GST_NZ': 15.00,   # New Zealand GST
        'GST_SG': 9.00,    # Singapore GST
        'GST_IN': 18.00,   # India GST (standard rate)
        'VAT_UK': 20.00,   # UK VAT
        'VAT_EU': 21.00,   # EU VAT (varies by country)
        'VAT_AE': 5.00,    # UAE VAT
        'VAT_SA': 15.00,   # Saudi Arabia VAT
        'VAT_BH': 10.00,   # Bahrain VAT
        'VAT_OM': 5.00,    # Oman VAT
        'VAT_QA': 0.00,    # Qatar (no VAT currently)
        'VAT_KW': 0.00,    # Kuwait (no VAT currently)
        'VAT_ZA': 15.00,   # South Africa VAT
    }

    @classmethod
    def get_currency_symbol(cls, currency_code):
        """Get currency symbol for a given currency code"""
        if currency_code in cls.CURRENCIES:
            return cls.CURRENCIES[currency_code]['symbol']
        return currency_code  # Return code itself if unknown

    @classmethod
    def get_currency_name(cls, currency_code):
        """Get currency name for a given currency code"""
        if currency_code in cls.CURRENCIES:
            return cls.CURRENCIES[currency_code]['name']
        return currency_code

    @classmethod
    def get_all_currencies(cls):
        """Get all supported currencies as a list for dropdowns"""
        return [
            {
                'code': code,
                'symbol': data['symbol'],
                'name': data['name'],
                'display': f"{code} ({data['symbol']}) - {data['name']}"
            }
            for code, data in cls.CURRENCIES.items()
        ]

    # Invoice Template Settings
    invoice_prefix = db.Column(db.String(20), default='INV')  # Invoice number prefix
    invoice_footer = db.Column(db.Text)  # Footer text for invoices
    invoice_notes = db.Column(db.Text)  # Default notes/terms
    invoice_bank_details = db.Column(db.Text)  # Bank account details for payment
    invoice_payment_terms = db.Column(db.String(100), default='Due within 14 days')

    # Invoice Section Visibility (all default to True)
    invoice_show_logo = db.Column(db.Boolean, default=True)
    invoice_show_company_details = db.Column(db.Boolean, default=True)
    invoice_show_client_details = db.Column(db.Boolean, default=True)
    invoice_show_bank_details = db.Column(db.Boolean, default=True)
    invoice_show_payment_terms = db.Column(db.Boolean, default=True)
    invoice_show_notes = db.Column(db.Boolean, default=True)
    invoice_show_footer = db.Column(db.Boolean, default=True)
    invoice_show_tax = db.Column(db.Boolean, default=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_company')
    users = db.relationship('User', foreign_keys='User.company_id', backref='company', lazy='dynamic')

    def to_dict(self, include_owner=True, include_stats=False):
        """Convert company to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'trading_name': self.trading_name,
            'abn': self.abn,
            'acn': self.acn,
            'email': self.email,
            'phone': self.phone,
            'website': self.website,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'postcode': self.postcode,
                'country': self.country
            },
            'plan_type': self.plan_type,
            'max_users': self.max_users,
            'max_clients': self.max_clients,
            'is_active': self.is_active,
            'company_type': self.company_type,
            'logo_url': self.logo_url,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'tertiary_color': self.tertiary_color,
            'sidebar_bg_color': self.sidebar_bg_color,
            'sidebar_text_color': self.sidebar_text_color,
            'sidebar_hover_bg_color': self.sidebar_hover_bg_color,
            'currency_settings': {
                'currency': self.currency,
                'currency_symbol': self.currency_symbol or self.CURRENCY_SYMBOLS.get(self.currency, '$'),
                'tax_type': self.tax_type,
                'tax_label': self.tax_label,
                'default_tax_rate': float(self.default_tax_rate) if self.default_tax_rate else 10.00
            },
            'invoice_settings': {
                'prefix': self.invoice_prefix,
                'footer': self.invoice_footer,
                'notes': self.invoice_notes,
                'bank_details': self.invoice_bank_details,
                'payment_terms': self.invoice_payment_terms,
                # Section visibility
                'show_logo': self.invoice_show_logo if self.invoice_show_logo is not None else True,
                'show_company_details': self.invoice_show_company_details if self.invoice_show_company_details is not None else True,
                'show_client_details': self.invoice_show_client_details if self.invoice_show_client_details is not None else True,
                'show_bank_details': self.invoice_show_bank_details if self.invoice_show_bank_details is not None else True,
                'show_payment_terms': self.invoice_show_payment_terms if self.invoice_show_payment_terms is not None else True,
                'show_notes': self.invoice_show_notes if self.invoice_show_notes is not None else True,
                'show_footer': self.invoice_show_footer if self.invoice_show_footer is not None else True,
                'show_tax': self.invoice_show_tax if self.invoice_show_tax is not None else True,
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_owner and self.owner:
            data['owner'] = {
                'id': self.owner.id,
                'email': self.owner.email,
                'full_name': self.owner.full_name
            }

        if include_stats:
            from app.modules.user.models import Role
            data['user_count'] = self.users.count()
            data['client_count'] = self.users.join(Role).filter(Role.name == Role.USER).count()
            data['accountant_count'] = self.users.join(Role).filter(Role.name == Role.ACCOUNTANT).count()

        return data

    def __repr__(self):
        return f'<Company {self.name}>'
