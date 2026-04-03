from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class User(models.Model):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (VIEWER, "Viewer"),
        (ANALYST, "Analyst"),
        (ADMIN, "Admin"),
    ]

    # Role hierarchy — used in permission checks
    ROLE_LEVELS = {VIEWER: 1, ANALYST: 2, ADMIN: 3}

    username = models.CharField(max_length=80, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=256)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=VIEWER)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    # DRF's IsAuthenticated permission checks these two properties.
    # Any User instance that comes out of the DB is by definition authenticated.
    is_authenticated = True
    is_anonymous = False

    def has_min_role(self, min_role):
        return self.ROLE_LEVELS.get(self.role, 0) >= self.ROLE_LEVELS.get(min_role, 99)

    def __str__(self):
        return f"{self.username} ({self.role})"


class FinancialRecord(models.Model):
    INCOME = "income"
    EXPENSE = "expense"

    TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
    ]

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=60)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete

    class Meta:
        db_table = "financial_records"
        ordering = ["-date", "-created_at"]

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def __str__(self):
        return f"{self.type} | {self.category} | {self.amount}"
