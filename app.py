from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import sqlite3, os, json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'designdhamaka-secret-2024')
DB = os.path.join(os.path.dirname(__file__), 'leads.db')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, email TEXT NOT NULL,
            phone TEXT, service TEXT, budget TEXT,
            message TEXT, status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'website',
            detail TEXT,
            service TEXT,
            delivery TEXT,
            link TEXT,
            image_filename TEXT,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
        # Seed default portfolio items if empty
        count = conn.execute('SELECT COUNT(*) FROM portfolio').fetchone()[0]
        if count == 0:
            items = [
                ('Vahan360','Trucks & Buses Exchange Platform','website',
                 "Delhi's #1 commercial vehicle marketplace with RC-verified listings, filter/search, buyer & seller login, and admin panel.",
                 'Website Development','6 Days','vahan360.com','project_vahan1.png',1),
                ('APEX MODS','Automotive Customization Studio','website',
                 "Premium website for Delhi's top car modification studio. Dark theme, red accents, service pages, gallery, and WhatsApp appointment booking.",
                 'Website Development','5 Days','apexmods.in','project_apex1.png',2),
                ('APEX MODS','Hero Section & Animations','website',
                 "Bold full-screen hero with animated stats counter, dual CTA, and car imagery overlay built for maximum first impression.",
                 'Website + UI Design','5 Days','apexmods.in','project_apex2.png',3),
                ('Revanta Regency','Boutique Hotel — Rooms & Booking','website',
                 "Luxury hotel website with live room availability checker, photo gallery, room-type pages, and seamless booking integration.",
                 'Website + Branding','7 Days','revantaregency.in','project_revanta1.png',4),
                ('Revanta Regency','Amenities & Guest Reviews','website',
                 "Full amenities section with icon cards, guest review carousel, and premium gold-on-cream design. 100% mobile responsive.",
                 'Website Design','7 Days','revantaregency.in','project_revanta2.png',5),
                ('Multiple Clients','Social Media Marketing Creatives','design',
                 "50+ social media posts, restaurant ads, food promos, fashion content, and event flyers across Canva and Photoshop for real clients.",
                 'Graphic Design + Social','Ongoing','@the.designdhamaka','collage.png',6),
            ]
            for i in items:
                conn.execute('INSERT INTO portfolio (title,description,category,detail,service,delivery,link,image_filename,sort_order) VALUES (?,?,?,?,?,?,?,?,?)', i)
        conn.commit()

init_db()

# ── ROUTES ──────────────────────────────────────────────
@app.route('/')
def home():
    with get_db() as conn:
        projects = conn.execute('SELECT * FROM portfolio WHERE is_active=1 ORDER BY sort_order LIMIT 3').fetchall()
    return render_template('index.html', featured=projects)

@app.route('/services')
def services(): return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    with get_db() as conn:
        projects = conn.execute('SELECT * FROM portfolio WHERE is_active=1 ORDER BY sort_order').fetchall()
    return render_template('portfolio.html', projects=projects)

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/testimonials')
def testimonials(): return render_template('testimonials.html')

@app.route('/pricing')
def pricing(): return render_template('pricing.html')

@app.route('/blog')
def blog(): return render_template('blog.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip()
        phone = request.form.get('phone','').strip()
        service = request.form.get('service','').strip()
        budget = request.form.get('budget','').strip()
        message = request.form.get('message','').strip()
        if not name or not email or not message:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('contact'))
        with get_db() as conn:
            conn.execute('INSERT INTO leads (name,email,phone,service,budget,message) VALUES (?,?,?,?,?,?)',
                (name,email,phone,service,budget,message))
            conn.commit()
        flash('Thank you! We will get back to you within 24 hours.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ── ADMIN ────────────────────────────────────────────────
@app.route('/admin')
def admin():
    with get_db() as conn:
        leads_raw = conn.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
        portfolio_raw = conn.execute('SELECT * FROM portfolio ORDER BY sort_order').fetchall()
        leads = [dict(r) for r in leads_raw]
        portfolio_items = [dict(r) for r in portfolio_raw]
        stats = {
            'total_leads': len(leads),
            'new_leads': sum(1 for l in leads if l['status']=='new'),
            'total_projects': len(portfolio_items),
            'active_projects': sum(1 for p in portfolio_items if p['is_active']),
        }
    return render_template('admin.html', leads=leads, portfolio_items=portfolio_items, stats=stats)

@app.route('/admin/update-status/<int:lid>', methods=['POST'])
def update_status(lid):
    status = request.form.get('status','new')
    with get_db() as conn:
        conn.execute('UPDATE leads SET status=? WHERE id=?',(status,lid))
        conn.commit()
    flash(f'Lead #{lid} updated to "{status}".', 'success')
    return redirect(url_for('admin'))

# ── PORTFOLIO CRUD ───────────────────────────────────────
ALLOWED = {'png','jpg','jpeg','gif','webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED

def secure_name(filename):
    import re
    name = filename.rsplit('.',1)
    base = re.sub(r'[^\w\-]','_', name[0])[:40]
    ext = name[1].lower() if len(name)>1 else 'jpg'
    return f"{base}_{int(datetime.now().timestamp())}.{ext}"

@app.route('/admin/portfolio/add', methods=['POST'])
def portfolio_add():
    title = request.form.get('title','').strip()
    description = request.form.get('description','').strip()
    category = request.form.get('category','website').strip()
    detail = request.form.get('detail','').strip()
    service = request.form.get('service','').strip()
    delivery = request.form.get('delivery','').strip()
    link = request.form.get('link','').strip()
    image_filename = ''
    if 'image' in request.files:
        f = request.files['image']
        if f and f.filename and allowed_file(f.filename):
            fname = secure_name(f.filename)
            f.save(os.path.join(UPLOAD_FOLDER, fname))
            image_filename = fname
    if not title:
        flash('Project title is required.', 'error')
        return redirect(url_for('admin'))
    with get_db() as conn:
        max_order = conn.execute('SELECT MAX(sort_order) FROM portfolio').fetchone()[0] or 0
        conn.execute('''INSERT INTO portfolio (title,description,category,detail,service,delivery,link,image_filename,sort_order,is_active)
            VALUES (?,?,?,?,?,?,?,?,?,1)''',
            (title,description,category,detail,service,delivery,link,image_filename,max_order+1))
        conn.commit()
    flash(f'Project "{title}" added successfully!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/portfolio/edit/<int:pid>', methods=['POST'])
def portfolio_edit(pid):
    title = request.form.get('title','').strip()
    description = request.form.get('description','').strip()
    category = request.form.get('category','website').strip()
    detail = request.form.get('detail','').strip()
    service = request.form.get('service','').strip()
    delivery = request.form.get('delivery','').strip()
    link = request.form.get('link','').strip()
    with get_db() as conn:
        old = conn.execute('SELECT image_filename FROM portfolio WHERE id=?',(pid,)).fetchone()
        image_filename = old['image_filename'] if old else ''
        if 'image' in request.files:
            f = request.files['image']
            if f and f.filename and allowed_file(f.filename):
                fname = secure_name(f.filename)
                f.save(os.path.join(UPLOAD_FOLDER, fname))
                image_filename = fname
        conn.execute('''UPDATE portfolio SET title=?,description=?,category=?,detail=?,service=?,delivery=?,link=?,image_filename=?
            WHERE id=?''', (title,description,category,detail,service,delivery,link,image_filename,pid))
        conn.commit()
    flash(f'Project "{title}" updated!', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/portfolio/delete/<int:pid>', methods=['POST'])
def portfolio_delete(pid):
    with get_db() as conn:
        item = conn.execute('SELECT title FROM portfolio WHERE id=?',(pid,)).fetchone()
        conn.execute('DELETE FROM portfolio WHERE id=?',(pid,))
        conn.commit()
    flash(f'Project deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/portfolio/toggle/<int:pid>', methods=['POST'])
def portfolio_toggle(pid):
    with get_db() as conn:
        item = conn.execute('SELECT is_active,title FROM portfolio WHERE id=?',(pid,)).fetchone()
        new_state = 0 if item['is_active'] else 1
        conn.execute('UPDATE portfolio SET is_active=? WHERE id=?',(new_state,pid))
        conn.commit()
    state = 'shown' if new_state else 'hidden'
    flash(f'Project "{item["title"]}" is now {state}.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/portfolio/reorder', methods=['POST'])
def portfolio_reorder():
    order = request.json.get('order',[])
    with get_db() as conn:
        for i, pid in enumerate(order):
            conn.execute('UPDATE portfolio SET sort_order=? WHERE id=?',(i+1,pid))
        conn.commit()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
