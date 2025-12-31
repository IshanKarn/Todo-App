from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Create users table"

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    is_email_verified INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
            # Create otps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_otps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    otp TEXT NOT NULL,
                    expires_at DATETIME NOT NULL,
                    is_used INTEGER DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
        self.stdout.write(self.style.SUCCESS("Users and OTPs tables created"))
