import sys
from pathlib import Path
sys.path.insert(0, r'c:\Users\Yessine-PC\Desktop\pfev0\user-analytics-backend')
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

template_path = Path(r'c:\Users\Yessine-PC\Desktop\pfev0\user-analytics-backend\app\templates')
env = Environment(loader=FileSystemLoader(str(template_path)), autoescape=False)
tpl = env.get_template('premium_enterprise_report.html')
ctx = {
    'language':'fr',
    'report_type':'executive',
    'date_range':'2024-01-01 — 2024-01-31',
    'services_list':'ElJournal, Esports.tn',
    'generated_by':'Test User',
    'generated_timestamp':'2026-05-16 12:00 UTC',
    'active_users':'9 500',
    'global_churn_rate':'5.2',
    'arpu':'150.5',
    'executive_health_score':'A',
    'ai_confidence_score':86,
    'ai_source':'fallback',
    'strategic_priorities':'Priority 1',
    'predictive_forecast':'Forecast',
    'expected_kpi_improvements':'Improve',
    'sections_included':['summary'],
    'ai_summary':'Summary',
    'active_growth_pct':'12',
    'churn_delta_pct':'-0.4',
    'conversion_rate':'6.8',
    'conversion_delta':'1.2',
    'retention_d30':'45.2',
    'high_risk_pct':'302',
}
html = tpl.render(**ctx)
Path('C:/Users/Yessine-PC/Desktop/pfev0/tmp_xhtml2pdf.html').write_text(html, encoding='utf-8')
print('rendered html')
from io import BytesIO
buf = BytesIO()
status = pisa.CreatePDF(html, dest=buf, encoding='utf-8')
print('status err', status.err)
print(status.log)
