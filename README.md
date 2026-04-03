# Finance Dashboard API

A role-based finance dashboard backend built with Django and Django REST Framework.

---

## Stack

| | |
|---|---|
| **Framework** | Django 5 + Django REST Framework |
| **Auth** | JWT via `djangorestframework-simplejwt` |
| **Database** | SQLite (swap to Postgres with one settings change) |

---

## Setup

```bash
git clone <repo>
cd finance_dashboard

python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed          # creates users + sample records
python manage.py runserver
```

Server runs at `http://localhost:8000`.

### Seeded accounts

| Username | Password | Role     |
|----------|----------|----------|
| admin    | admin123 | admin    |
| alice    | alice123 | analyst  |
| bob      | bob123   | viewer   |

Change these before deploying anywhere.

---

## Roles

| Role     | What they can do |
|----------|-----------------|
| `viewer`   | Read records, view summary + recent activity |
| `analyst`  | Everything viewer can + create records + category breakdown + trends |
| `admin`    | Everything + update/delete records + manage users |

---

## API Reference

All protected routes require:
```
Authorization: Bearer <access_token>
```

---

### Auth

#### `POST /auth/login/`
```json
{ "username": "admin", "password": "admin123" }
```
Returns `access` token, `refresh` token, and `user` object.

#### `POST /auth/refresh/`
```json
{ "refresh": "<refresh_token>" }
```
Returns a new `access` token.

#### `GET /auth/me/`
Returns the currently authenticated user's profile.

---

### Users *(admin only)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/` | List all users |
| `POST` | `/users/` | Create a user |
| `GET` | `/users/<id>/` | Get a user by ID |
| `PUT` | `/users/<id>/` | Update a user (all fields optional) |
| `DELETE` | `/users/<id>/` | Delete a user |
| `PATCH` | `/users/<id>/status/` | Activate or deactivate a user |

**Create/update body:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secure123",
  "role": "analyst"
}
```

**Status toggle body:**
```json
{ "is_active": false }
```

---

### Financial Records

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/records/` | viewer+ | List records |
| `GET` | `/records/<id>/` | viewer+ | Get single record |
| `POST` | `/records/` | analyst+ | Create a record |
| `PUT` | `/records/<id>/` | admin | Update a record (partial ok) |
| `DELETE` | `/records/<id>/` | admin | Soft delete a record |

**Create/update body:**
```json
{
  "amount": "1200.00",
  "type": "expense",
  "category": "Rent",
  "date": "2024-03-01",
  "notes": "March rent"
}
```

**Query filters for `GET /records/`:**

| Param | Example | Notes |
|-------|---------|-------|
| `type` | `income` or `expense` | Exact match |
| `category` | `rent` | Case-insensitive partial match |
| `from_date` | `2024-01-01` | On or after |
| `to_date` | `2024-03-31` | On or before |
| `page` | `1` | Default: 1 |
| `per_page` | `20` | Default: 20, max: 100 |

**Example response:**
```json
{
  "records": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 42,
    "pages": 3
  }
}
```

---

### Dashboard

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `GET` | `/dashboard/summary/` | viewer+ | Income, expenses, net balance |
| `GET` | `/dashboard/recent/` | viewer+ | Latest N records |
| `GET` | `/dashboard/categories/` | analyst+ | Totals grouped by category |
| `GET` | `/dashboard/trends/` | analyst+ | Monthly income vs expense |

**`/dashboard/recent/`** — optional param: `?limit=10` (max 50)

**`/dashboard/trends/`** — optional param: `?months=6` (range: 1–24)

---

## Project Structure

```
finance_dashboard/
├── finance_dashboard/
│   ├── settings.py          # Config, DRF + JWT settings
│   └── urls.py              # Root URL routing
├── api/
│   ├── models.py            # User, FinancialRecord
│   ├── serializers.py       # Read/write serializers for both models
│   ├── permissions.py       # IsAdmin, IsAnalystOrAbove, IsViewerOrAbove
│   ├── backends.py          # Custom JWT backend for our User model
│   ├── utils.py             # Custom exception handler + pagination helper
│   ├── views/
│   │   ├── auth.py          # Login, token refresh, /me
│   │   ├── users.py         # User CRUD + status toggle
│   │   ├── records.py       # Financial records CRUD + filtering
│   │   └── dashboard.py     # Summary, categories, trends, recent
│   ├── urls/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── records.py
│   │   └── dashboard.py
│   └── management/
│       └── commands/
│           └── seed.py      # python manage.py seed
└── requirements.txt
```

---

## Design Decisions & Assumptions

**Custom User model instead of `AbstractUser`** — The assignment called for a clean, purpose-built model. Inheriting `AbstractUser` brings in ~15 fields we don't need (first name, last name, groups, permissions, etc.) and couples us to Django's auth system. The tradeoff is we need a custom JWT backend, which is a few lines.

**Separate read/write serializers** — `UserSerializer` and `FinancialRecordSerializer` are read-only and used for responses. `CreateUserSerializer`, `UpdateUserSerializer`, and `RecordWriteSerializer` handle input. This keeps validation logic clean and avoids weird `read_only_fields` gymnastics.

**Permission classes over middleware** — DRF's class-based permissions are composable and visible right at the view. Each view explicitly declares what level of access it requires, which makes auditing easier than chasing middleware chains.

**Soft deletes on records** — financial data shouldn't just disappear. Records get a `deleted_at` timestamp; all queries filter `deleted_at__isnull=True`. Hard deletes stay for users since there's no audit reason to keep them.

**`get_permissions()` per-method** — `RecordListView` and `RecordDetailView` use `get_permissions()` to return different permission classes based on the HTTP method. This avoids splitting one logical resource into two views just to differ on write access.

**SQLite for now, Postgres-ready** — The ORM query style (no raw SQL, uses `TruncMonth`, `Sum`, `Count`) works unchanged on Postgres. Switch is just one line in `settings.py`.

**Trends returns only months present in data** — If there are no records in February, that month won't appear. Returning empty rows for every calendar month felt like frontend work, not backend work.

**Pagination capped at 100** — Prevents someone from fetching the whole table in one request by accident. A `per_page=999` silently becomes 100.
