"""
PDF Generator for SMSF Audit Letters
Uses WeasyPrint to convert Jinja2 HTML templates to PDF.
"""
import os
import io
import base64
from datetime import datetime
from jinja2 import Environment, BaseLoader


def _load_logo_base64() -> str:
    """Load AusSuperSource logo as base64 for embedding in PDF."""
    # Try several possible paths relative to this file
    candidates = [
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'frontend', 'public', 'assets', 'aussupersource-logo.png'),
        os.path.join('/app', 'static', 'aussupersource-logo.png'),
        os.path.join(os.path.dirname(__file__), 'aussupersource-logo.png'),
    ]
    for path in candidates:
        path = os.path.normpath(path)
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
    return ''  # fallback: no logo image, CSS text header used instead


# ─── CSS shared across both letter types ────────────────────────────────────

LETTER_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}
* { box-sizing: border-box; }
body {
    font-family: Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #1a1a1a;
    margin: 0;
    padding: 0;
}
.header-logo {
    text-align: right;
    margin-bottom: 20px;
    border-bottom: 3px solid #1B72BE;
    padding-bottom: 10px;
}
.header-logo .company-name {
    font-size: 18pt;
    font-weight: bold;
    color: #1B72BE;
    display: block;
}
.header-logo .company-sub {
    font-size: 9pt;
    color: #666;
}
h1 {
    font-size: 14pt;
    font-weight: bold;
    color: #1A2E5A;
    text-align: center;
    margin: 16px 0 10px 0;
    text-decoration: underline;
}
h2 {
    font-size: 12pt;
    font-weight: bold;
    color: #1A2E5A;
    margin: 14px 0 4px 0;
}
p {
    margin: 0 0 8px 0;
}
.date-line {
    text-align: right;
    margin-bottom: 16px;
    font-size: 11pt;
}
.addressee {
    margin-bottom: 16px;
}
.addressee .fund-name {
    font-weight: bold;
}
.section-title {
    font-weight: bold;
    text-decoration: underline;
    margin: 14px 0 4px 0;
}
ol {
    margin: 0 0 8px 16px;
    padding: 0;
}
ol li {
    margin-bottom: 6px;
}
ul {
    margin: 0 0 8px 20px;
    padding: 0;
}
ul li {
    margin-bottom: 4px;
}
.signature-section {
    margin-top: 30px;
}
.signature-block {
    display: inline-block;
    width: 48%;
    vertical-align: top;
    margin-bottom: 20px;
    border: 1px solid #ccc;
    padding: 12px;
    border-radius: 4px;
}
.signature-block:nth-child(even) {
    margin-left: 4%;
}
.signature-label {
    font-size: 9pt;
    color: #555;
    margin-bottom: 2px;
}
.signature-image {
    height: 60px;
    max-width: 200px;
    display: block;
    margin: 6px 0;
    border-bottom: 1px solid #333;
}
.signature-line {
    border-bottom: 1px solid #333;
    height: 50px;
    margin: 6px 0;
    display: block;
}
.signature-name {
    font-weight: bold;
    font-size: 10pt;
    margin-top: 4px;
}
.signature-role {
    font-size: 9pt;
    color: #555;
}
.signature-date {
    font-size: 9pt;
    color: #555;
    margin-top: 4px;
}
.page-break {
    page-break-before: always;
}
table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
}
td, th {
    padding: 6px 8px;
    border: 1px solid #ccc;
    font-size: 10pt;
    vertical-align: top;
}
th {
    background-color: #1A2E5A;
    color: white;
    font-weight: bold;
}
.highlight-box {
    background-color: #f0f7ff;
    border-left: 4px solid #1B72BE;
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 10pt;
}
.footer-note {
    font-size: 9pt;
    color: #666;
    border-top: 1px solid #ccc;
    padding-top: 8px;
    margin-top: 20px;
}
"""


# ─── Engagement Letter Template ──────────────────────────────────────────────

ENGAGEMENT_LETTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{{ css }}</style>
</head>
<body>

<div class="header-logo">
    {% if logo_b64 %}
    <img src="data:image/png;base64,{{ logo_b64 }}" alt="AusSuperSource" style="height:55px; max-width:220px; object-fit:contain;">
    {% else %}
    <span class="company-name">AusSuperSource</span>
    {% endif %}
    <span class="company-sub" style="display:block;">SMSF Auditors | ABN 50 122 940 596 | info@aussupersource.com.au | aussupersource.com.au</span>
</div>

<h1>ENGAGEMENT LETTER — SMSF AUDIT</h1>

<div class="date-line">{{ letter_date }}</div>

<div class="addressee">
    <p class="fund-name">The Trustees of<br>{{ fund_name }}</p>
    {% if address_line1 %}<p>{{ address_line1 }}{% if address_line2 %}<br>{{ address_line2 }}{% endif %}<br>
    {% if city or state or postcode %}{{ city }}{% if state %} {{ state }}{% endif %}{% if postcode %} {{ postcode }}{% endif %}{% endif %}</p>{% endif %}
</div>

<p>Dear Trustee(s),</p>

<p>We are pleased to confirm our engagement to provide audit services to <strong>{{ fund_name }}</strong>
(the "Fund") for the financial year ended <strong>{{ financial_year_end }}</strong>
(period {{ period_start }} to {{ financial_year_end }}).</p>

<p>This letter sets out the terms and conditions of our engagement. Please read it carefully and
sign and return the acknowledgment at the end of this letter to confirm your acceptance of these terms.</p>

<h2>1. OBJECTIVE AND SCOPE OF THE AUDIT</h2>

<p>The objective of our audit is to enable us to express an opinion on whether:</p>
<ol type="a">
    <li>The financial statements of the Fund present fairly the financial position of the Fund as at
    {{ financial_year_end }}, and the results of its operations and cash flows for the year then ended,
    in accordance with the Australian Accounting Standards and other mandatory professional reporting requirements; and</li>
    <li>The Fund has, in all material respects, complied with the requirements of the
    <em>Superannuation Industry (Supervision) Act 1993</em> (SISA), the
    <em>Superannuation Industry (Supervision) Regulations 1994</em> (SISR), and the trust deed of the Fund.</li>
</ol>

<p>Our audit will be conducted in accordance with Australian Auditing Standards and the
<em>ASIC Regulatory Guide 268: Reporting on SMSF Audits</em>.</p>

<h2>2. AUDITOR'S RESPONSIBILITIES</h2>

<p>Our responsibilities as auditor are to:</p>
<ol>
    <li>Conduct an independent audit of the Fund's financial statements for the financial year ended
    {{ financial_year_end }};</li>
    <li>Conduct a compliance audit to determine whether the Fund has complied with the relevant
    provisions of SISA and SISR;</li>
    <li>Issue an audit report (SMSF Independent Auditor's Report — Form 131) which will include an
    opinion on the financial statements and a conclusion on compliance; and</li>
    <li>Lodge the audit report with the Australian Taxation Office (ATO) as required.</li>
</ol>

<p>An audit involves performing procedures to obtain audit evidence about the amounts and disclosures
in the financial statements. The procedures selected depend on the auditor's judgement, including
the assessment of the risks of material misstatement of the financial statements, whether due to
fraud or error. An audit also includes evaluating the appropriateness of accounting policies used
and the reasonableness of accounting estimates made by the trustees, as well as evaluating the
overall presentation of the financial statements.</p>

<p>We believe that the audit evidence we obtain will be sufficient and appropriate to provide a
basis for our audit opinion.</p>

<h2>3. TRUSTEE'S RESPONSIBILITIES</h2>

<p>As trustees of the Fund, you are responsible for:</p>
<ol>
    <li>The preparation and fair presentation of the financial statements in accordance with
    Australian Accounting Standards;</li>
    <li>Such internal control as you determine is necessary to enable the preparation of financial
    statements that are free from material misstatement, whether due to fraud or error;</li>
    <li>Ensuring the Fund complies with the requirements of SISA, SISR, and the Fund's trust deed;</li>
    <li>Providing us with access to all information of which you are aware that is relevant to the
    preparation of the financial statements, such as records, documentation, and other matters;</li>
    <li>Providing us with additional information that we may request from you for the purpose of the audit;</li>
    <li>Providing unrestricted access to persons within the Fund from whom we determine it necessary
    to obtain audit evidence;</li>
    <li>Providing us with a signed Trustee Representation Letter prior to the issue of the audit report; and</li>
    <li>Maintaining the Fund's books and records in a manner that is readily accessible and auditable.</li>
</ol>

<h2>4. AUDIT FEES</h2>

<div class="highlight-box">
    <p>Our fee for conducting the SMSF audit for the financial year ended <strong>{{ financial_year_end }}</strong>
    is outlined below. All fees are exclusive of GST.</p>
</div>

<table>
    <tr>
        <th>Service</th>
        <th style="text-align:right;">Fee (excl. GST)</th>
    </tr>
    <tr>
        <td>SMSF Annual Audit — {{ fund_name }}</td>
        <td style="text-align:right;">${{ audit_fee }}</td>
    </tr>
    <tr>
        <td><strong>Total</strong></td>
        <td style="text-align:right;"><strong>${{ audit_fee }}</strong></td>
    </tr>
</table>

<p>Our fees are based on the complexity of the Fund and the time required to complete the audit.
We will invoice you upon completion of the audit. Payment is due within 14 days of the invoice date.
If additional work is required due to incomplete records or other issues, we will advise you
of any additional charges before proceeding.</p>

<h2>5. INDEPENDENCE</h2>

<p>We confirm that we are independent of the Fund and its trustees in accordance with the
requirements of the APES 110 Code of Ethics for Professional Accountants as they apply to SMSF auditors.
We are not aware of any matters that would impair our independence.</p>

<p>Our ASIC-registered SMSF auditor details:</p>
<ul>
    <li><strong>Auditor Name:</strong> {{ auditor_name }}</li>
    <li><strong>ASIC Registration Number:</strong> {{ auditor_registration }}</li>
</ul>

<h2>6. CONFIDENTIALITY</h2>

<p>We confirm that all information obtained in the course of our engagement is held in strict
confidence in accordance with our professional obligations. We will not disclose any information
to third parties without your prior consent, except where required by law or professional standards
(including mandatory reporting obligations under section 129 of SISA).</p>

<h2>7. REPORTING OBLIGATIONS</h2>

<p>Under section 129 of SISA, we are required to report to the ATO if we become aware that a
contravention of SISA or SISR has occurred, may have occurred, or is likely to occur. We are
also required to report if the financial position of the Fund is, or may be, unsatisfactory.
These obligations exist regardless of whether the contravention has been or will be rectified.</p>

<h2>8. LIMITATION OF LIABILITY</h2>

<p>Our liability is limited by a scheme approved under Professional Standards Legislation. Further
information on the scheme is available from the Professional Standards Councils website.</p>

<h2>9. COMPLAINTS</h2>

<p>If you have any concerns about our services, please contact us in the first instance.
If the matter is not resolved, you may contact ASIC, the Tax Practitioners Board (TPB), or
Chartered Accountants Australia and New Zealand (CA ANZ) / CPA Australia, as applicable.</p>

<h2>10. ACCEPTANCE</h2>

<p>If the terms set out in this letter are acceptable to you, please sign and return the enclosed
copy of this letter. Your signature confirms that you:</p>
<ol type="a">
    <li>Have read and understood the terms of this engagement letter;</li>
    <li>Accept the responsibilities outlined in section 3 above; and</li>
    <li>Authorise us to proceed with the audit on these terms.</li>
</ol>

<p>We look forward to working with you and thank you for engaging AusSuperSource to conduct your
SMSF audit for the financial year ended {{ financial_year_end }}.</p>

<p>Yours sincerely,</p>

<div class="signature-block">
    <div class="signature-label">On behalf of AusSuperSource</div>
    <div class="signature-label" style="margin-top:8px;">Auditor Name: <strong>{{ auditor_name }}</strong></div>
    <div class="signature-label">ASIC Registration: <strong>{{ auditor_registration }}</strong></div>
    <div class="signature-label" style="margin-top:8px;">Date: {{ letter_date }}</div>
</div>

<div class="page-break"></div>

<!-- ─── Trustee Acceptance ─────────────────────────── -->

<h1>TRUSTEE ACCEPTANCE</h1>

<p>We, the undersigned trustees of <strong>{{ fund_name }}</strong>, acknowledge receipt of and agree
to the terms and conditions of the engagement letter dated <strong>{{ letter_date }}</strong>.</p>

<div class="signature-section">
{% for trustee in trustees %}
<div class="signature-block">
    <div class="signature-label">Trustee Signature</div>
    {% if trustee.signature_b64 %}
    <img class="signature-image" src="data:image/png;base64,{{ trustee.signature_b64 }}" alt="Signature">
    {% else %}
    <div class="signature-line"></div>
    {% endif %}
    <div class="signature-name">{{ trustee.name }}</div>
    {% if trustee.company %}<div class="signature-role">{{ trustee.company }}</div>{% endif %}
    {% if trustee.role %}<div class="signature-role">{{ trustee.role }}</div>{% endif %}
    <div class="signature-date">Date: {% if trustee.signed_date %}{{ trustee.signed_date }}{% else %}________________{% endif %}</div>
</div>
{% if loop.index is even and not loop.last %}<div style="clear:both;"></div>{% endif %}
{% endfor %}
</div>

<div class="footer-note">
    <p>AusSuperSource Pty Ltd | ABN 50 122 940 596 | info@aussupersource.com.au | aussupersource.com.au</p>
    <p>ASIC Registered SMSF Auditor | {{ auditor_name }} | Registration No. {{ auditor_registration }}</p>
</div>

</body>
</html>
"""


# ─── Representation Letter Template ─────────────────────────────────────────

REPRESENTATION_LETTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>{{ css }}</style>
</head>
<body>

<div class="header-logo">
    {% if logo_b64 %}
    <img src="data:image/png;base64,{{ logo_b64 }}" alt="AusSuperSource" style="height:55px; max-width:220px; object-fit:contain;">
    {% else %}
    <span class="company-name">AusSuperSource</span>
    {% endif %}
    <span class="company-sub" style="display:block;">SMSF Auditors | ABN 50 122 940 596 | info@aussupersource.com.au | aussupersource.com.au</span>
</div>

<h1>TRUSTEE REPRESENTATION LETTER</h1>

<div class="date-line">{{ letter_date }}</div>

<div class="addressee">
    <p>{{ auditor_name }}<br>
    ASIC Registered SMSF Auditor<br>
    {% if auditor_address %}{{ auditor_address|replace('\n','<br>')|safe }}{% else %}AusSuperSource<br>info@aussupersource.com.au{% endif %}</p>
</div>

<p>Dear {{ auditor_name }},</p>

<p>We are writing in connection with your audit of the financial statements of
<strong>{{ fund_name }}</strong> (the "Fund") for the financial year ended
<strong>{{ financial_year_end }}</strong> (period {{ period_start }} to {{ financial_year_end }}).</p>

<p>We confirm, to the best of our knowledge and belief, having made appropriate enquiries, the
following representations made to you during your audit:</p>

<h2>FINANCIAL STATEMENTS</h2>

<ol>
    <li>We have fulfilled our responsibilities for the preparation and fair presentation of the
    financial statements in accordance with Australian Accounting Standards. We believe the
    financial statements give a true and fair view of the financial position and performance
    of the Fund for the year ended {{ financial_year_end }}.</li>

    <li>We have provided you with access to all information relevant to the preparation of the
    financial statements, including all accounting records and supporting documentation,
    and all board/trustee minutes.</li>

    <li>We have disclosed to you the results of our assessment of the risk that the financial
    statements may be materially misstated as a result of fraud.</li>

    <li>We have disclosed to you all information in relation to fraud or suspected fraud that
    we are aware of and that affects the Fund, involving management, employees who have
    significant roles in internal control, or others where the fraud could have a material
    effect on the financial statements.</li>

    <li>We have disclosed to you all known instances of non-compliance or suspected non-compliance
    with laws and regulations whose effects should be considered when preparing the financial statements.</li>

    <li>We have disclosed to you all known actual or possible litigation and claims whose effects
    should be considered when preparing the financial statements.</li>

    <li>All transactions have been recorded in the accounting records and are reflected in the
    financial statements.</li>

    <li>We have no plans or intentions that may materially affect the carrying values or
    classification of assets and liabilities reflected in the financial statements.</li>
</ol>

<h2>ASSETS AND LIABILITIES</h2>

<ol start="9">
    <li>The Fund holds legal title to, or has enforceable rights to, all assets reflected in
    the financial statements. There are no liens, encumbrances, pledges, or assignments on
    the Fund's assets, other than those disclosed in the financial statements.</li>

    <li>All liabilities of the Fund as at {{ financial_year_end }} have been recorded and
    disclosed in the financial statements. There are no undisclosed liabilities as at that date.</li>

    <li>All investments held by the Fund as at {{ financial_year_end }} are valued at fair value
    in accordance with Australian Accounting Standards. Valuations have been obtained from
    independent and authoritative sources where available (e.g. market prices, licensed valuers).</li>

    <li>All cash and bank accounts held by or for the benefit of the Fund have been disclosed.
    All bank reconciliations as at {{ financial_year_end }} have been completed.</li>

    <li>The Fund does not hold any assets on behalf of a third party, nor are any of the Fund's
    assets held by a third party as custodian, other than as disclosed.</li>
</ol>

<h2>COMPLIANCE WITH SIS ACT AND REGULATIONS</h2>

<ol start="14">
    <li>The Fund has at all times during the financial year ending {{ financial_year_end }} been
    and remains an "Australian superannuation fund" as defined in section 10 of the SISA, satisfying
    the residency rules.</li>

    <li>The Fund's trust deed is current and compliant with current superannuation legislation.
    No amendments to the trust deed have been made during the financial year, other than as disclosed.</li>

    <li>All contributions received during the year were permissible contributions under the SISA and SISR.
    No contributions in breach of contribution limits or restrictions have been accepted.</li>

    <li>All benefit payments made during the financial year were made in accordance with the SISA,
    SISR, the Fund's trust deed, and the conditions of release applicable to each member.</li>

    <li>The Fund has complied with the investment strategy requirements of section 52B of the SISA.
    The investment strategy was reviewed during the financial year and all investments were made
    in accordance with that strategy.</li>

    <li>The Fund has complied with the in-house asset rules under Part 8 of the SISA. The
    in-house asset ratio of the Fund as at {{ financial_year_end }} did not exceed 5% of the
    Fund's total assets.</li>

    <li>No assets of the Fund have been acquired from a related party of the Fund during the year,
    other than assets that are permitted to be acquired from related parties under section 66 of
    the SISA (i.e. listed securities, business real property, or in-house assets within the 5% limit).</li>

    <li>No assets of the Fund have been used to provide financial assistance to a member or
    relative of a member of the Fund in contravention of section 65 of the SISA.</li>

    <li>The Fund has not borrowed money or maintained borrowings during the year, except as
    permitted under a limited recourse borrowing arrangement (LRBA) compliant with section 67A
    of the SISA, as disclosed in the financial statements.</li>

    <li>All members of the Fund are individual trustees or directors of the corporate trustee,
    and all trustee consent, appointment, and removal requirements have been met in accordance
    with the SISA and trust deed.</li>

    <li>The Fund has lodged, or will lodge, its Annual Return with the ATO for the financial year
    ended {{ financial_year_end }} on time, including the Member Contributions Statement.</li>

    <li>We have maintained and will make available all records, accounts, and documentation
    required under the SISA and SISR, including minutes of all trustee meetings and decisions
    for the financial year ended {{ financial_year_end }}.</li>

    <li>We are not aware of any contraventions of the SISA or SISR during the financial year
    ended {{ financial_year_end }}, other than any matters already brought to your attention
    or disclosed in the financial statements.</li>
</ol>

<h2>SUBSEQUENT EVENTS</h2>

<p>There have been no events subsequent to {{ financial_year_end }} which would require adjustment
to, or disclosure in, the financial statements, other than events already disclosed.</p>

<h2>GOING CONCERN</h2>

<p>The Fund is a going concern. We are not aware of any matters that may cast significant doubt
on the Fund's ability to continue as a going concern.</p>

<p>This letter has been signed by all trustees of the Fund.</p>

<div class="signature-section">
{% for trustee in trustees %}
<div class="signature-block">
    <div class="signature-label">Trustee Signature</div>
    {% if trustee.signature_b64 %}
    <img class="signature-image" src="data:image/png;base64,{{ trustee.signature_b64 }}" alt="Signature">
    {% else %}
    <div class="signature-line"></div>
    {% endif %}
    <div class="signature-name">{{ trustee.name }}</div>
    {% if trustee.company %}<div class="signature-role">{{ trustee.company }}</div>{% endif %}
    {% if trustee.role %}<div class="signature-role">{{ trustee.role }}</div>{% endif %}
    <div class="signature-date">Date: {% if trustee.signed_date %}{{ trustee.signed_date }}{% else %}________________{% endif %}</div>
</div>
{% if loop.index is even and not loop.last %}<div style="clear:both;"></div>{% endif %}
{% endfor %}
</div>

<div class="footer-note">
    <p>AusSuperSource Pty Ltd | ABN 50 122 940 596 | info@aussupersource.com.au | aussupersource.com.au</p>
    <p>ASIC Registered SMSF Auditor | {{ auditor_name }} | Registration No. {{ auditor_registration }}</p>
</div>

</body>
</html>
"""


# ─── Generator class ─────────────────────────────────────────────────────────

class LetterPDFGenerator:
    """Generate PDF from letter data using WeasyPrint + Jinja2."""

    TEMPLATES = {
        'engagement': ENGAGEMENT_LETTER_HTML,
        'representation': REPRESENTATION_LETTER_HTML,
    }

    @classmethod
    def render_html(cls, letter_type: str, context: dict) -> str:
        """Render Jinja2 HTML template with the given context."""
        template_str = cls.TEMPLATES.get(letter_type)
        if not template_str:
            raise ValueError(f"Unknown letter type: {letter_type}")

        env = Environment(loader=BaseLoader(), autoescape=False)
        template = env.from_string(template_str)
        context['css'] = LETTER_CSS
        return template.render(**context)

    @classmethod
    def generate_pdf_bytes(cls, letter_type: str, context: dict) -> bytes:
        """Render HTML and convert to PDF bytes using WeasyPrint."""
        from weasyprint import HTML, CSS
        html_content = cls.render_html(letter_type, context)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    @classmethod
    def build_context(cls, letter, entity) -> dict:
        """Build the Jinja2 context dict from an AuditLetter record and its ClientEntity."""
        fy = letter.financial_year or ''
        try:
            fy_int = int(fy)
            period_start = f"01/07/{fy_int - 1}"
            financial_year_end = f"30/06/{fy_int}"
        except (ValueError, TypeError):
            period_start = ''
            financial_year_end = fy

        trustees = letter.trustees_data or []
        if not trustees:
            trustees = [{'name': entity.trustee_name or 'Trustee', 'company': '', 'role': 'Trustee',
                         'signature_b64': None, 'signed_date': None}]

        return {
            'letter_date': letter.letter_date or datetime.utcnow().strftime('%d %B %Y'),
            'fund_name': entity.name,
            'address_line1': entity.address_line1 or '',
            'address_line2': entity.address_line2 or '',
            'city': entity.city or '',
            'state': entity.state or '',
            'postcode': entity.postcode or '',
            'financial_year_end': financial_year_end,
            'period_start': period_start,
            'auditor_name': letter.auditor_name or 'AusSuperSource',
            'auditor_registration': letter.auditor_registration or '',
            'auditor_address': letter.auditor_address or 'AusSuperSource\ninfo@aussupersource.com.au',
            'audit_fee': '400',
            'trustees': trustees,
            'logo_b64': _load_logo_base64(),
        }
