todo_app_django/
│
├── auth_app/
│   ├── api/                     # 🔐 API layer (JSON)
│   │   ├── views.py             # login, register, otp, logout
│   │   ├── urls.py              # /api/auth/*
│   │   └── permissions.py
│   │
│   ├── ui/                      # 🖥️ Jinja UI layer
│   │   ├── views.py             # render templates, call APIs
│   │   └── urls.py              # /login, /register, /reset
│   │
│   ├── templates/
│   │   └── auth/                # auth-specific templates
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── verify_email.html
│   │       ├── forgot_password.html
│   │       └── reset_password.html
│   │
│   ├── authentication.py        # JWT auth
│   ├── jwt_utils.py
│   ├── security.py
│   ├── logger.py
│   ├── utils.py                 # email validation, helpers
│   └── management/
│       └── commands/
│
├── tasks/
│   ├── api/
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── ui/
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── templates/tasks/
│       └── tasks.html
│
├── templates/
│   └── base.html                # shared layout
│
├── todo_project/
│   ├── settings.py
│   └── urls.py
│
└── manage.py
