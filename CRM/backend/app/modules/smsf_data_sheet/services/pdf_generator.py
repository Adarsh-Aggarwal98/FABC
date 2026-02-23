"""
PDF Generator for SMSF Basic Data Sheet
Produces a filled PDF using dynamic loops — handles any number of members/trustees.
"""
import os
import base64
from jinja2 import Environment, BaseLoader


def _load_logo_b64() -> str:
    candidates = [
        os.path.normpath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', '..', 'frontend', 'public', 'assets', 'aussupersource-logo.png'
        )),
        '/app/static/aussupersource-logo.png',
    ]
    for p in candidates:
        if os.path.exists(p):
            with open(p, 'rb') as f:
                return base64.b64encode(f.read()).decode()
    return ''


CSS = """
@page {
    size: A4;
    margin: 1.8cm 1.5cm 1.8cm 1.5cm;
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 8pt; color: #888;
    }
}
* { box-sizing: border-box; }
body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #111; margin: 0; }

.header { display: flex; justify-content: space-between; align-items: flex-end;
          border-bottom: 3px solid #1B72BE; padding-bottom: 8px; margin-bottom: 14px; }
.header-company { font-size: 16pt; font-weight: bold; color: #1B72BE; }
.header-sub { font-size: 8pt; color: #666; }

h1 { text-align: center; font-size: 14pt; font-weight: bold; color: #1A2E5A;
     background: #e8f0fb; padding: 7px; margin: 0 0 12px 0; }
h2 { background: #1A2E5A; color: white; font-size: 10pt; font-weight: bold;
     padding: 5px 8px; margin: 12px 0 0 0; }

table { width: 100%; border-collapse: collapse; margin-bottom: 0; }
td, th { border: 1px solid #bbb; padding: 4px 6px; font-size: 9.5pt; vertical-align: top; }

.label  { font-weight: bold; background: #f5f7fa; white-space: nowrap; }
.value  { background: #fff; }
.source { font-size: 8pt; color: #888; background: #f9f9f9; text-align: center;
          vertical-align: middle; width: 12%; }

.row-head { background: #1B72BE; color: white; font-weight: bold;
            text-align: center; padding: 4px; }

.events-head { background: #1A2E5A; color: white; font-weight: bold;
               padding: 4px 6px; font-size: 9.5pt; }

.page-break { page-break-before: always; }
.footer { font-size: 8pt; color: #888; border-top: 1px solid #ccc;
          padding-top: 6px; margin-top: 14px; text-align: center; }
"""

TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>{{ css }}</style></head>
<body>

<!-- HEADER -->
<div class="header">
  <div>
    {% if logo_b64 %}
    <img src="data:image/png;base64,{{ logo_b64 }}" alt="AusSuperSource" style="height:46px;">
    {% else %}
    <div class="header-company">AusSuperSource</div>
    {% endif %}
    <div class="header-sub">SMSF Auditors | ABN 50 122 940 596 | info@aussupersource.com.au</div>
  </div>
  <div style="text-align:right;font-size:9pt;color:#555;">
    Financial Year: <strong>FY{{ financial_year }}</strong><br>
    Period: 01/07/{{ financial_year|int - 1 }} – 30/06/{{ financial_year }}
  </div>
</div>

<h1>SMSF BASIC DATA SHEET</h1>

<!-- FUND DETAILS -->
<table>
  <tr>
    <td class="label" style="width:22%">Name of SMSF</td>
    <td class="value" colspan="2"><strong>{{ fund_name }}</strong></td>
    <td class="source">Trust Deed</td>
  </tr>
  <tr>
    <td class="label">Date of Creation</td>
    <td class="value">{{ date_of_creation }}</td>
    <td class="source">Trust Deed</td>
    <td></td>
  </tr>
  <tr>
    <td class="label">ABN of SMSF</td>
    <td class="value">{{ abn_of_smsf }}</td>
    <td class="source">ATO ABN Letter</td>
    <td></td>
  </tr>
  <tr>
    <td class="label">TFN of SMSF</td>
    <td class="value">{{ tfn_of_smsf }}</td>
    <td class="source">ATO TFN Letter</td>
    <td></td>
  </tr>
</table>

<!-- MEMBERS (dynamic — pairs side by side) -->
<h2>Members' Detail ({{ members|length }} member{{ 's' if members|length != 1 else '' }})</h2>
{% for pair_start in range(0, members|length, 2) %}
{% set m1 = members[pair_start] %}
{% set m2 = members[pair_start + 1] if pair_start + 1 < members|length else None %}
<table style="margin-bottom:4px;">
  <tr>
    <td class="row-head" colspan="3">Member {{ pair_start + 1 }}{% if m1.name %} — {{ m1.name }}{% endif %}</td>
    {% if m2 %}
    <td class="row-head" colspan="3">Member {{ pair_start + 2 }}{% if m2.name %} — {{ m2.name }}{% endif %}</td>
    {% else %}
    <td colspan="3" style="border:0;"></td>
    {% endif %}
  </tr>
  <tr>
    <td class="label" style="width:12%">Name</td>
    <td class="value" style="width:30%"><strong>{{ m1.name }}</strong></td>
    <td class="source" style="width:8%">Trust deed</td>
    <td class="label" style="width:12%">Name</td>
    <td class="value" style="width:30%"><strong>{{ m2.name if m2 else '' }}</strong></td>
    <td class="source" style="width:8%">{% if m2 %}Trust deed{% endif %}</td>
  </tr>
  <tr>
    <td class="label">Address</td>
    <td class="value" style="white-space:pre-wrap;">{{ m1.address }}</td>
    <td class="source">Trust deed</td>
    <td class="label">Address</td>
    <td class="value" style="white-space:pre-wrap;">{{ m2.address if m2 else '' }}</td>
    <td class="source">{% if m2 %}Trust deed{% endif %}</td>
  </tr>
  <tr>
    <td class="label">DOB</td>
    <td class="value">{{ m1.dob }}</td>
    <td class="source"></td>
    <td class="label">DOB</td>
    <td class="value">{{ m2.dob if m2 else '' }}</td>
    <td class="source"></td>
  </tr>
  <tr>
    <td class="label">TFN</td>
    <td class="value">{{ m1.tfn }}</td>
    <td class="source"></td>
    <td class="label">TFN</td>
    <td class="value">{{ m2.tfn if m2 else '' }}</td>
    <td class="source"></td>
  </tr>
  <tr>
    <td class="label">Date of Joining</td>
    <td class="value">{{ m1.date_of_joining }}</td>
    <td class="source">Trust deed</td>
    <td class="label">Date of Joining</td>
    <td class="value">{{ m2.date_of_joining if m2 else '' }}</td>
    <td class="source">{% if m2 %}Trust deed{% endif %}</td>
  </tr>
</table>
{% endfor %}
{% if not members %}
<table><tr><td style="color:#999;font-style:italic;padding:6px;">No members recorded.</td></tr></table>
{% endif %}

<!-- TRUSTEES (dynamic — pairs side by side) -->
<h2>Trustee Details ({{ trustees|length }} trustee{{ 's' if trustees|length != 1 else '' }})</h2>
{% for pair_start in range(0, trustees|length, 2) %}
{% set t1 = trustees[pair_start] %}
{% set t2 = trustees[pair_start + 1] if pair_start + 1 < trustees|length else None %}
<table style="margin-bottom:4px;">
  <tr>
    <td class="row-head" colspan="3">Trustee {{ pair_start + 1 }}{% if t1.name %} — {{ t1.name }}{% endif %}</td>
    {% if t2 %}
    <td class="row-head" colspan="3">Trustee {{ pair_start + 2 }}{% if t2.name %} — {{ t2.name }}{% endif %}</td>
    {% else %}
    <td colspan="3" style="border:0;"></td>
    {% endif %}
  </tr>
  <tr>
    <td class="label" style="width:12%">Name</td>
    <td class="value" style="width:30%"><strong>{{ t1.name }}</strong></td>
    <td class="source" style="width:8%">Trust deed</td>
    <td class="label" style="width:12%">Name</td>
    <td class="value" style="width:30%"><strong>{{ t2.name if t2 else '' }}</strong></td>
    <td class="source" style="width:8%">{% if t2 %}Trust deed{% endif %}</td>
  </tr>
  <tr>
    <td class="label">Address</td>
    <td class="value" style="white-space:pre-wrap;">{{ t1.address }}</td>
    <td class="source">Trust deed</td>
    <td class="label">Address</td>
    <td class="value" style="white-space:pre-wrap;">{{ t2.address if t2 else '' }}</td>
    <td class="source">{% if t2 %}Trust deed{% endif %}</td>
  </tr>
  <tr>
    <td class="label">ACN (if Co)</td>
    <td class="value">{{ t1.acn }}</td>
    <td class="source">Trust deed</td>
    <td class="label">ACN (if Co)</td>
    <td class="value">{{ t2.acn if t2 else '' }}</td>
    <td class="source">{% if t2 %}Trust deed{% endif %}</td>
  </tr>
</table>
{% endfor %}
{% if not trustees %}
<table><tr><td style="color:#999;font-style:italic;padding:6px;">No trustees recorded.</td></tr></table>
{% endif %}

<!-- PAGE BREAK before Bare Trustee -->
<div class="page-break"></div>

<!-- BARE TRUSTEE -->
<h2>Bare Trustee Details</h2>
<table>
  <tr>
    <td class="label" style="width:22%">Bare Trust Name</td>
    <td class="value" colspan="3">{{ bare_trustee.bare_trust_name }}</td>
  </tr>
  <tr>
    <td class="label">Bare Trustee</td>
    <td class="value" colspan="3">{{ bare_trustee.bare_trustee_name }}</td>
  </tr>
  <tr>
    <td class="label">Address</td>
    <td class="value" colspan="3" style="white-space:pre-wrap;">{{ bare_trustee.address }}</td>
  </tr>
  <tr>
    <td class="label">A.C.N. (if Co)</td>
    <td class="value" colspan="3">{{ bare_trustee.acn }}</td>
  </tr>
</table>

<!-- NOMINATIONS (one block per member, dynamic) -->
<h2>Nomination Details</h2>
{% if not members %}
<table><tr><td style="color:#999;font-style:italic;padding:6px;">No members — no nominations.</td></tr></table>
{% else %}
{% for i in range(members|length) %}
{% set m = members[i] %}
{% set noms = nominations[i] if nominations|length > i else [] %}
<div style="margin-bottom:6px;">
  <table>
    <tr>
      <td class="row-head" colspan="3">
        Member {{ i + 1 }}{% if m.name %} — {{ m.name }}{% endif %}
      </td>
    </tr>
    <tr>
      <th class="label" style="width:45%">Nominee – Relation</th>
      <th class="label" style="width:15%; text-align:center;">%age</th>
      <th style="border:0; width:40%;"></th>
    </tr>
    {% for n in noms %}
    <tr>
      <td class="value">{{ n.nominee }}{% if n.relation %} – {{ n.relation }}{% endif %}</td>
      <td class="value" style="text-align:center;">{{ n.percentage }}</td>
      <td style="border:0;"></td>
    </tr>
    {% endfor %}
    {% if not noms %}
    <tr>
      <td class="value" style="color:#999;font-style:italic;">No nominations recorded</td>
      <td class="value"></td>
      <td style="border:0;"></td>
    </tr>
    {% endif %}
  </table>
</div>
{% endfor %}
{% endif %}

<!-- PAGE BREAK before Subsequent Events -->
<div class="page-break"></div>

<!-- SUBSEQUENT EVENTS -->
<h2>Subsequent Events</h2>
<table>
  <tr>
    <td class="events-head" style="width:22%">Date</td>
    <td class="events-head">Name of Event</td>
  </tr>
  {% for ev in subsequent_events %}
  <tr>
    <td class="value" style="height:22px;">{{ ev.date }}</td>
    <td class="value">{{ ev.name_of_event }}</td>
  </tr>
  {% endfor %}
  {% set pad = 10 - subsequent_events|length %}
  {% for _ in range(pad if pad > 0 else 0) %}
  <tr>
    <td class="value" style="height:22px;">&nbsp;</td>
    <td class="value">&nbsp;</td>
  </tr>
  {% endfor %}
</table>

<div class="footer">
  AusSuperSource Pty Ltd | ABN 50 122 940 596 | info@aussupersource.com.au | aussupersource.com.au
</div>
</body></html>
"""


class DataSheetPDFGenerator:

    @classmethod
    def render_html(cls, ctx: dict) -> str:
        env  = Environment(loader=BaseLoader(), autoescape=False)
        tmpl = env.from_string(TEMPLATE)
        ctx.setdefault('css', CSS)
        ctx.setdefault('logo_b64', _load_logo_b64())
        return tmpl.render(**ctx)

    @classmethod
    def generate_pdf_bytes(cls, ctx: dict) -> bytes:
        from weasyprint import HTML
        return HTML(string=cls.render_html(ctx)).write_pdf()

    @classmethod
    def build_context(cls, sheet) -> dict:
        members  = sheet.members  or []
        trustees = sheet.trustees or []
        noms     = list(sheet.nominations or [])
        # ensure one nominations sub-list per member
        while len(noms) < len(members):
            noms.append([])

        return {
            'financial_year':    sheet.financial_year,
            'fund_name':         sheet.fund_name        or '',
            'date_of_creation':  sheet.date_of_creation or '',
            'abn_of_smsf':       sheet.abn_of_smsf      or '',
            'tfn_of_smsf':       sheet.tfn_of_smsf      or '',
            'members':           members,
            'trustees':          trustees,
            'bare_trustee':      sheet.bare_trustee      or {},
            'nominations':       noms[:len(members)],
            'subsequent_events': sheet.subsequent_events or [],
        }
