from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Create task tables"

    def handle(self, *args, **kwargs):
       # Create tasks table
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date DATE,
                    status TEXT DEFAULT 'pending',
                    user_id INTEGER REFERENCES users(id)
                )
            """)
        self.stdout.write(self.style.SUCCESS("Tasks table created successfully"))