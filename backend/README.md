# UniMart Backend

This backend folder is dedicated to the Django + PostgreSQL implementation for the UniMart marketplace.

## Structure

- `backend/` – Django project settings and entry points
- `marketplace/` – main app with models, views, URLs, and admin registration
- `db.sqlite3` – local database for development
- `requirements.txt` – Python dependencies

## Run locally

From the project root:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Then visit:

- http://localhost:8000/health/

## Notes

This is a clean backend separation so the frontend and backend are handled in their own folders.
