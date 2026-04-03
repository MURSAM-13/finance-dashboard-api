"""
Usage: python manage.py seed

Seeds a default admin account and sample financial records.
Safe to run multiple times — checks before inserting.
"""

from datetime import date
from django.core.management.base import BaseCommand
from api.models import User, FinancialRecord


SAMPLE_RECORDS = [
    dict(amount=5000, type="income",  category="Salary",     date=date(2024, 1, 5),  notes="January salary"),
    dict(amount=1200, type="expense", category="Rent",        date=date(2024, 1, 10)),
    dict(amount=300,  type="expense", category="Utilities",   date=date(2024, 1, 15)),
    dict(amount=5000, type="income",  category="Salary",      date=date(2024, 2, 5),  notes="February salary"),
    dict(amount=1200, type="expense", category="Rent",        date=date(2024, 2, 10)),
    dict(amount=450,  type="expense", category="Groceries",   date=date(2024, 2, 18)),
    dict(amount=800,  type="income",  category="Freelance",   date=date(2024, 2, 22), notes="Design project"),
    dict(amount=5000, type="income",  category="Salary",      date=date(2024, 3, 5),  notes="March salary"),
    dict(amount=1200, type="expense", category="Rent",        date=date(2024, 3, 10)),
    dict(amount=200,  type="expense", category="Transport",   date=date(2024, 3, 20)),
]


class Command(BaseCommand):
    help = "Seed the database with an admin user and sample financial records"

    def handle(self, *args, **kwargs):
        admin = self._create_user("admin", "admin@example.com", "admin123", User.ADMIN)
        self._create_user("alice", "alice@example.com", "alice123", User.ANALYST)
        self._create_user("bob", "bob@example.com", "bob123", User.VIEWER)

        if not FinancialRecord.objects.exists():
            for data in SAMPLE_RECORDS:
                FinancialRecord.objects.create(created_by=admin, **data)
            self.stdout.write(f"  Created {len(SAMPLE_RECORDS)} sample records")
        else:
            self.stdout.write("  Records already exist, skipping")

        self.stdout.write(self.style.SUCCESS("\nSeed complete."))
        self.stdout.write("  admin   / admin123  (admin)")
        self.stdout.write("  alice   / alice123  (analyst)")
        self.stdout.write("  bob     / bob123    (viewer)")

    def _create_user(self, username, email, password, role):
        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  User '{username}' already exists, skipping")
            return User.objects.get(username=username)

        user = User(username=username, email=email, role=role)
        user.set_password(password)
        user.save()
        self.stdout.write(f"  Created user: {username} ({role})")
        return user
