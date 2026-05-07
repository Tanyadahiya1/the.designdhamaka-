# the.designdhamaka — Website

## Local Setup
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000

## Deploy to Render
1. Push code to GitHub
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - **Environment:** Python 3
5. Add env var: `SECRET_KEY` = any random string
6. Click Deploy!

## Admin Panel
Visit `/admin` to view all contact form submissions.

## Pages
- `/` — Home
- `/services` — Services
- `/portfolio` — Portfolio
- `/about` — About
- `/pricing` — Pricing
- `/testimonials` — Testimonials
- `/blog` — Blog
- `/contact` — Contact Form
- `/admin` — Leads Dashboard
