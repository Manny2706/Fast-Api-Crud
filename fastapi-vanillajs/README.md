# FastAPI + Vanilla JS Demo

Quick demo implementing JWT auth, role-based access, and CRUD for `Task`.


Setup (recommended in a venv):

```powershell
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
uvicorn fastapi_app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

Frontend: open `frontend/index.html` and point the JS to `http://127.0.0.1:8000` (default).

Database options:

- Development (default): uses SQLite file `db.sqlite3`. No extra setup required.

- Production (Postgres): run Postgres via Docker Compose and set environment variables. Example:

```powershell
docker-compose up -d
# copy .env.example to .env and edit SECRET_KEY
setx DATABASE_URL "postgresql+psycopg2://primetrade:primetradepass@127.0.0.1:5432/primetrade"
setx SECRET_KEY "<secure-random-key>"
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000
```

Notes:
- The app reads `DATABASE_URL` env var; if not set it falls back to SQLite. Use `SECRET_KEY` env var in production.
- For Docker-based production, adjust connection host from `db` to your DB host as needed.
