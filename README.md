# ECELL Hackathon Web App

This repository contains a small Flask web application hackathon platform.
It provides user and admin dashboards, team creation and membership, announcements, and a live leaderboard (score updates).

## Features

- User registration and login
- User dashboard: create teams, add members (team leader), view announcements
- Team model with leader and members
- Score model per team and a leaderboard
- Admin dashboard: post announcements, update team scores, view users
- Seeded sample data for quick testing

## Seeded accounts (for development)

- Admin: `username: admin` / `password: admin123`
- Sample users:
  - `alice@example.com` / `password`
  - `bob@example.com` / `password`

Note: these are created by `create_db.py` when you run it (development only).

## Project layout (key files)

- `app.py` — small runner that calls `website.create_app()`
- `create_db.py` — creates the DB and seeds sample data
- `requirements.txt` — Python dependencies
- `website/__init__.py` — Flask app factory and SQLAlchemy init
- `website/models.py` — SQLAlchemy models (User, Admin, Team, Score, Announcement)
- `website/routes.py` — all Flask routes / views
- `website/templates/` — Jinja2 templates (Bootstrap-based)

## Quick start (macOS / zsh)

1. Open a terminal and cd into the project root (where `app.py` is):

```bash
cd /Users/macklinchrissmiranda/Desktop/ECELL_tasks
```

2. (Recommended) Create a virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

4. Create and seed the database (this creates `hackathon.db`):

```bash
python3 create_db.py
```

You should see `Database created/seeded.` when successful. If you see `ModuleNotFoundError: No module named 'flask'`, ensure your virtualenv is activated and dependencies installed into the same interpreter you use to run the script.

5. Run the app:

```bash
python3 app.py
```

Visit http://127.0.0.1:5000 in your browser.

## Useful endpoints

- `/` — Home (announcements + top teams)
- `/register` — User registration
- `/login` — User login
- `/dashboard` — User dashboard (requires login)
- `/team/create` — Create a team (requires login)
- `/team/<id>` — Team page (leader can add members)
- `/leaderboard` — Leaderboard
- `/admin/login` — Admin login
- `/admin/dashboard` — Admin dashboard (requires admin login)
- `/admin/users` — List all users (admin)

## Changing admin password or creating another admin

Open a Python shell with the app context (recommended):

```bash
python3
>>> from website import create_app, db
>>> app = create_app()
>>> ctx = app.app_context()
>>> ctx.push()
>>> from website.models import Admin
>>> a = Admin(username='newadmin')
>>> a.set_password('newpassword')
>>> db.session.add(a)
>>> db.session.commit()
>>> ctx.pop()
```

Or update the seeded admin in `create_db.py` and re-run (careful not to overwrite live data).

## Troubleshooting

- ModuleNotFoundError: No module named 'flask' — activate the correct venv and install `requirements.txt` into that interpreter.
- Database not appearing — check you ran `create_db.py` and that `website/__init__.py` uses `sqlite:///hackathon.db` (should be the default).

## Next steps / Improvements

- Add migrations (Flask-Migrate / Alembic) for schema changes
- Add tests (pytest) and basic CI
- Implement WebSocket or Server-Sent Events for real-time leaderboard updates
- Merge `Admin` into `User` with a role field if you prefer unified accounts

## License

This project is provided as-is for hackathon/demo use. Update as needed.

---

If you'd like, I can also:
- Create a `README` in the repo automatically (done here) and commit & push it, or
- Add a simple `Dockerfile` and `docker-compose.yml` for local containerized runs.

Tell me which one you prefer and I will proceed.
