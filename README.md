📝 Django ToDo App (Raw SQL + JWT + OTP)

ToDo application built using Django + Django REST Framework.

📁 Project Structure
todo_app_django/
│
├── auth_app/          # Authentication (JWT, OTP, Email) APIs + UI
├── tasks/             # Task CRUD APIs + UI
├── templates/         # Shared templates (base.html) + index.html
├── manage.py
├── requirements.txt
└── README.md

🚀 Project Setup

### Clone Repository
```bash
git clone https://github.com/IshanKarn/Todo-App.git
cd todo_app
```

### Create Virtual Environment
```bash
python -m venv venv
```

### Activate Virtual Environment:

Windows
```bash
venv\Scripts\activate
```

Mac / Linux
```bash
source venv/bin/activate
```
### Install Requirements
```bash
pip install -r requirements.txt
```

### Database Setup (SQLite)

This project uses SQLite with raw SQL tables (no Django models).

Run Django Migrations - create sqlite db
```bash
python manage.py migrate
```
Creates DB: db.sqlite3

### Create Application Tables (Raw SQL)

Run the custom management commands:
```bash
python manage.py init_users
python manage.py init_tasks
```

Creates tables: users, tasks, password_otps

### Run Development Server
```bash
python manage.py runserver
```

Access app at: http://127.0.0.1:8000/

### Authentication Flow

Register

Email OTP verification

Login → JWT issued

JWT required for all task APIs

Password reset via OTP

### Swagger API Documentation

Swagger UI (OpenAPI 3): http://127.0.0.1:8000/api/docs/
OpenAPI schema (JSON): http://127.0.0.1:8000/api/schema/

### JWT supported via Authorize button:
```bash
Authorization: Bearer <access_token>
```

### Running Tests

Run all tests
```bash
python manage.py test
```
Run auth tests only
```bash
python manage.py test auth_app
```
Run task tests only
```bash
python manage.py test tasks
```