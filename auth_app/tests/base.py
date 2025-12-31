from django.test import TestCase
from django.db import connection

class RawSQLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        with connection.cursor() as cursor:

            # USERS TABLE
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_email_verified BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # TASKS TABLE
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date DATE,
                    status TEXT DEFAULT 'pending',
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # OTP TABLE
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_otps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    otp TEXT NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    expires_at DATETIME NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
