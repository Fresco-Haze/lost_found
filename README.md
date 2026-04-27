# 🔍 CampusFind

> A smart Lost & Found platform for university campuses — built with Flask, SQLite, and Africa's Talking SMS.

Students and staff can report lost or found items, browse listings, get auto-matched by category, and receive real-time SMS notifications when a potential match is found.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 Auth | Email-restricted login/register (`@students.ku.ac.ke`) |
| 📦 Item Reporting | Report **lost** or **found** items with photo uploads |
| 🔍 Browse & Filter | Search by keyword, filter by status or category |
| 🤝 Auto Matching | Items in the same category are automatically paired |
| 📲 SMS Alerts | Africa's Talking SMS sent when a match is found |
| 🛡️ Admin Panel | Manage items, users, match approvals |
| 🌙 Dark / Light Mode | Persisted via `localStorage` |

---

## 🏗️ Project Structure

```
lost_found/
├── app.py              # App factory (create_app)
├── config.py           # All configuration constants
├── extensions.py       # Shared Flask extensions (db)
├── models.py           # SQLAlchemy models: User, Item, Match
├── utils.py            # Africa's Talking SMS helper
├── seed.py             # DB seeding script
├── .env                # Environment variables (never commit!)
│
├── routes/
│   ├── __init__.py
│   ├── auth.py         # /login  /register  /logout
│   ├── items.py        # /  /report_*  /item/<id>  /my-items  /matches  /profile
│   └── admin.py        # /admin  /admin/item/*  /admin/user/*
│
├── templates/
│   ├── base.html       # Layout, flash messages, shared JS
│   ├── login.html
│   ├── register.html
│   ├── index.html      # Browse listings
│   ├── item_detail.html
│   ├── my_items.html
│   ├── matches.html
│   ├── profile.html
│   ├── admin.html
│   └── admin_edit.html
│
└── static/
    ├── style.css
    └── uploads/        # User-uploaded item images
```

---

## 🚀 Setup & Run

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/your-username/campusfind.git
cd campusfind
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install flask flask-sqlalchemy werkzeug python-dotenv requests
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-very-secret-key
AT_USERNAME=sandbox
AT_API_KEY=your-africas-talking-api-key
```

### 4. Run the development server

```bash
python app.py
```

Then open [http://localhost:5000](http://localhost:5000)

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session secret — change for production |
| `AT_USERNAME` | ✅ | Africa's Talking username (`sandbox` for testing) |
| `AT_API_KEY` | ✅ | Africa's Talking API key |

---

## 🗺️ Roadmap

- [x] User registration & login (domain-restricted)
- [x] Report lost / found items with image upload
- [x] Auto-matching by category
- [x] SMS notifications via Africa's Talking
- [x] Admin dashboard (items + users + matches)
- [ ] **Email verification** (next milestone)
- [ ] Password reset flow
- [ ] WhatsApp notifications
- [ ] Match scoring (location + date proximity)
- [ ] Mobile app (React Native)

---

## 🛡️ Security Notes

- Passwords are hashed with **Werkzeug** (PBKDF2-SHA256)
- Only `@students.ku.ac.ke` emails are accepted at registration
- Admin actions are protected by session-based `admin_required` decorator
- Never commit your `.env` file — add it to `.gitignore`

---

## 📄 License

MIT © 2025 — Kenyatta University CampusFind Team
