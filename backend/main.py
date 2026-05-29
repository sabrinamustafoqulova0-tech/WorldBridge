"""
main.py — WorldBridge Backend entry-point.

Stack:
  • FastAPI          — web framework
  • SQLAlchemy async — ORM (PostgreSQL via asyncpg)
  • JWT              — authentication (python-jose)
  • Uvicorn          — ASGI server

Run locally:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Docs:
    http://localhost:8000/docs   ← Swagger UI
    http://localhost:8000/redoc  ← ReDoc
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

# ── Internal imports ──────────────────────────────────────────────────────────
from config import settings
from database import Base, engine

# All feature routers
from routers import auth, articles, calculator, checklists, favorites, programs, users


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup  → create all tables that don't exist yet.
                  In production, use `alembic upgrade head` instead.
    On shutdown → gracefully close the DB connection pool.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


# ── Application factory ───────────────────────────────────────────────────────

def create_app() -> FastAPI:
    app = FastAPI(
        # ── Metadata (shown in Swagger UI) ────────────────────────────────
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "## WorldBridge REST API\n\n"
            "Backend for the **WorldBridge** relocation portal — programs, articles, "
            "favourites, checklists and an integrated cost calculator.\n\n"
            "### Programs covered\n"
            "Ausbildung · FSJ · Au Pair · Schule · Arbeit · Studium\n\n"
            "### Auth\n"
            "Use **POST /api/v1/auth/login** to obtain a Bearer token, "
            "then click **Authorize** (🔒) and paste it."
        ),
        docs_url="/docs",        # Swagger UI
        redoc_url="/redoc",      # ReDoc
        openapi_url="/openapi.json",
        contact={
            "name": "WorldBridge Team",
            "url": "https://WorldBridge.com",
            "email": "dev@WorldBridge.com",
        },
        license_info={
            "name": "MIT",
        },
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────

    # GZip — compress responses > 1 KB automatically
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS — allow the Next.js frontend + production domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",          # Next.js dev server
            "http://127.0.0.1:3000",
            *settings.ALLOWED_ORIGINS,        # extra origins from .env
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers (all under /api/v1) ───────────────────────────────────────────
    PREFIX = "/api/v1"

    app.include_router(auth.router,       prefix=PREFIX)   # /api/v1/auth
    app.include_router(users.router,      prefix=PREFIX)   # /api/v1/users
    app.include_router(programs.router,   prefix=PREFIX)   # /api/v1/programs
    app.include_router(articles.router,   prefix=PREFIX)   # /api/v1/articles
    app.include_router(favorites.router,  prefix=PREFIX)   # /api/v1/favorites
    app.include_router(calculator.router, prefix=PREFIX)   # /api/v1/calculator
    app.include_router(checklists.router, prefix=PREFIX)   # /api/v1/checklists

    # ── Health check ──────────────────────────────────────────────────────────

    @app.get(
        "/health",
        tags=["Health"],
        summary="Health check",
        response_description="Returns API status and current version",
    )
    async def health() -> JSONResponse:
        """
        Lightweight liveness probe.

        - Returns **200 OK** with `{"status": "ok"}` when the server is running.
        - Used by Docker / Kubernetes health checks and load balancers.
        """
        return JSONResponse(
            content={"status": "ok", "version": settings.APP_VERSION},
            status_code=200,
        )

    return app


# ── ASGI app instance ─────────────────────────────────────────────────────────
app = create_app()
