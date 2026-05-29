# WorldBridge Backend

> **FastAPI** REST API for the [WorldBridge](https://WorldBridge.com) portal —
> your guide to relocation programs in Germany: **Ausbildung · FSJ · Au Pair · Schule · Arbeit · Studium**.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Auth** | JWT access + refresh tokens, bcrypt hashing, admin roles |
| **Programs** | Full CRUD for all 6 program categories with slug, search & view counter |
| **Applications** | Users apply to programs; admins manage status workflow |
| **Articles** | Blog/guides with admin CMS |
| **DB** | PostgreSQL via async SQLAlchemy 2.0 + Alembic migrations |
| **Tests** | Pytest-asyncio with in-memory SQLite — no external DB needed |
| **Docker** | Multi-stage Dockerfile + docker-compose with Postgres & Redis |

---

## 🗂️ Project Structure

```
WorldBridge-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py        ← aggregates all routers
│   │       ├── auth.py            ← /register /login /refresh /me
│   │       ├── programs.py        ← /programs (CRUD + search)
│   │       ├── applications.py    ← /applications
│   │       ├── users.py           ← /users (profile + admin)
│   │       └── articles.py        ← /articles (blog)
│   ├── core/
│   │   ├── config.py              ← pydantic-settings
│   │   ├── security.py            ← JWT + bcrypt
│   │   └── dependencies.py        ← FastAPI deps (current_user, admin)
│   ├── db/
│   │   └── session.py             ← async engine, Base, get_db
│   ├── models/                    ← SQLAlchemy ORM models
│   ├── schemas/                   ← Pydantic request/response schemas
│   ├── repositories/              ← DB query layer
│   └── main.py                    ← FastAPI app factory
├── alembic/                       ← DB migrations
├── scripts/
│   └── seed.py                    ← seed admin + sample programs
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_programs.py
│   └── test_applications.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

---

## 🚀 Quick Start (Local)

### 1. Clone & create virtual env
```bash
cd WorldBridge-backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY
```

### 4. Start PostgreSQL (via Docker)
```bash
docker-compose up -d db redis
```

### 5. Run migrations
```bash
alembic upgrade head
```

### 6. Seed the database
```bash
python scripts/seed.py
```

### 7. Start the server
```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** — interactive Swagger UI is ready! 🎉

---

## 🐳 Docker (Full Stack)

```bash
docker-compose up --build
```

All three services (API + PostgreSQL + Redis) start together.

---

## ✅ Running Tests

```bash
pytest
```

Tests use an **in-memory SQLite** database — no external services required.

---

## 📡 API Endpoints Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/v1/auth/register` | — | Register new user |
| `POST` | `/api/v1/auth/login` | — | Login, get tokens |
| `POST` | `/api/v1/auth/refresh` | — | Refresh access token |
| `GET` | `/api/v1/auth/me` | User | Own profile |
| `GET` | `/api/v1/programs` | — | List programs (filter, search) |
| `GET` | `/api/v1/programs/{slug}` | — | Get program detail |
| `POST` | `/api/v1/programs` | Admin | Create program |
| `PATCH` | `/api/v1/programs/{id}` | Admin | Update program |
| `DELETE` | `/api/v1/programs/{id}` | Admin | Delete program |
| `POST` | `/api/v1/applications` | User | Apply to program |
| `GET` | `/api/v1/applications/my` | User | My applications |
| `DELETE` | `/api/v1/applications/my/{id}` | User | Withdraw application |
| `GET` | `/api/v1/applications` | Admin | All applications |
| `PATCH` | `/api/v1/applications/{id}` | Admin | Update status |
| `GET` | `/api/v1/articles` | — | List articles |
| `GET` | `/api/v1/articles/{slug}` | — | Get article |
| `POST` | `/api/v1/articles` | Admin | Create article |
| `GET` | `/health` | — | Health check |

---

## 🌍 Program Categories

| Category | Description |
|---|---|
| `ausbildung` | Vocational training (dual system) |
| `fsj` | Freiwilliges Soziales Jahr (voluntary service) |
| `au_pair` | Au Pair with host family |
| `schule` | School exchange year |
| `arbeit` | Skilled worker immigration |
| `studium` | University study in Germany |

---

## 🔐 Default Admin Credentials (seed)

| Field | Value |
|---|---|
| Email | `admin@WorldBridge.com` |
| Password | `Admin1234!` |

> ⚠️ Change immediately in production!

---

## 🛠️ Tech Stack

- **Python 3.12** · **FastAPI 0.115** · **SQLAlchemy 2.0 (async)**
- **PostgreSQL 16** · **Alembic** · **Redis 7**
- **JWT (python-jose)** · **bcrypt (passlib)**
- **Pytest + pytest-asyncio** · **Docker / docker-compose**
