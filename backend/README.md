# SUHAASA Backend — Milestone 1

This is the first backend foundation for the approved SUHAASA V15 frontend.

## Stack
- Django
- Django REST Framework
- PostgreSQL-ready configuration
- SQLite default for the first local setup
- Django Admin
- CORS support

## Current scope
- Category model
- Product model
- Product variants / inventory
- Product images
- Admin registration
- Health endpoint
- Product/category read APIs
- Demo seed command

## Local setup (PowerShell)

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo_products
python manage.py createsuperuser
python manage.py runserver
```

API:
- http://127.0.0.1:8000/api/health/
- http://127.0.0.1:8000/api/products/
- http://127.0.0.1:8000/api/products/categories/
- http://127.0.0.1:8000/admin/

## PostgreSQL

The project is already structured so we can switch the local/prod database to PostgreSQL by setting `DB_ENGINE=postgresql` and the DB variables in `.env`.

Do not commit `.env`.
