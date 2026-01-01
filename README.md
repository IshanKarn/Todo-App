# 📝 Django ToDo App (Raw SQL + JWT + OTP)

ToDo application built using Django + Django REST Framework.

### 📁 Project Structure
```text
todo_app_django/
│
├── auth_app/          # Authentication (JWT, OTP, Email) APIs + UI
├── tasks/             # Task CRUD APIs + UI
├── templates/         # Shared templates (base.html) + index.html
├── manage.py
├── requirements.txt
├── db.sqlite3
├── README.md
└── .env
```

### 🚀 Project Setup

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

### Create .env file to store secrets
Create .env file in root directory
Copy and paste environment variables from .env.example file 
Update values of variables (refer below for maif config)

### Mail config
Setup google app password
Visit https://myaccount.google.com/apppasswords
Write App Name - Todo
Click on Create
Copy generated app password
Set app password as EMAIL_HOST_PASSWORD value in .env file
Set gmail as value of EMAIL_HOST_USER in .env file

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

### Postman collection
Collection file in root directory: Todo App.postman_collection.json

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