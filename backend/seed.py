"""
seed.py — Populate the database with an admin user and sample programs.

Usage (from the WorldBridge-backend/ directory):
    python seed.py
"""

import asyncio
import logging

from sqlalchemy import select

from config import settings
from database import AsyncSessionLocal, Base, engine
from models.article import Article  # noqa: F401 – register model
from models.checklist import ChecklistItem  # noqa: F401
from models.favorite import Favorite  # noqa: F401
from models.program import Program, ProgramCategory, ProgramLevel  # noqa: F401
from models.user import User
from utils.jwt import hash_password

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ── Sample data ───────────────────────────────────────────────────────────────

SAMPLE_PROGRAMS = [
    {
        "slug": "ausbildung-it-specialist",
        "title": "IT-Spezialist Ausbildung",
        "category": ProgramCategory.AUSBILDUNG,
        "level": ProgramLevel.BEGINNER,
        "short_description": "Become a certified IT specialist in Germany through a dual vocational training program.",
        "description": (
            "The Ausbildung zum Fachinformatiker is a 3-year dual vocational training combining "
            "practical work at a German company with theory at a vocational school (Berufsschule). "
            "You earn a salary from day one and receive a recognised German qualification at the end."
        ),
        "duration_months": 36,
        "min_age": 16,
        "max_age": 35,
        "language_requirement": "B1/B2",
        "salary_range": "600–1 100 €/month",
        "is_published": True,
    },
    {
        "slug": "fsj-social-work",
        "title": "FSJ — Freiwilliges Soziales Jahr",
        "category": ProgramCategory.FSJ,
        "level": ProgramLevel.BEGINNER,
        "short_description": "Spend a voluntary social year in Germany helping communities and improving your German.",
        "description": (
            "The Freiwilliges Soziales Jahr (FSJ) is a 6–18 month voluntary service program for "
            "young people aged 16–27. Participants work in hospitals, schools, or social facilities "
            "and receive pocket money, accommodation, food, and social insurance coverage."
        ),
        "duration_months": 12,
        "min_age": 16,
        "max_age": 27,
        "language_requirement": "A2/B1",
        "salary_range": "200–650 €/month (pocket money)",
        "is_published": True,
    },
    {
        "slug": "au-pair-germany",
        "title": "Au Pair in Deutschland",
        "category": ProgramCategory.AU_PAIR,
        "level": ProgramLevel.BEGINNER,
        "short_description": "Live with a German host family, help with childcare, and immerse yourself in the language.",
        "description": (
            "The Au Pair program allows young people aged 18–26 to live with a German host family "
            "for 12 months (extendable to 24). Au Pairs assist with childcare up to 30 hours/week "
            "and receive board, lodging, and a monthly pocket money of at least 280 €."
        ),
        "duration_months": 12,
        "min_age": 18,
        "max_age": 26,
        "language_requirement": "A1",
        "salary_range": "280 €/month + room & board",
        "is_published": True,
    },
    {
        "slug": "studium-bachelor-germany",
        "title": "Bachelor-Studium in Deutschland",
        "category": ProgramCategory.STUDIUM,
        "level": ProgramLevel.INTERMEDIATE,
        "short_description": "Study at a German university — tuition-free in most federal states.",
        "description": (
            "Germany offers world-class bachelor's degrees, mostly tuition-free at public universities. "
            "International applicants need language certificates (German or English programs), "
            "school-leaving documents, and sometimes an aptitude test (Aufnahmeprüfung)."
        ),
        "duration_months": 36,
        "min_age": 18,
        "max_age": None,
        "language_requirement": "B2/C1",
        "salary_range": "No tuition (semester fee ~300 €)",
        "is_published": True,
    },
    {
        "slug": "arbeit-skilled-worker",
        "title": "Fachkraft — Arbeit in Deutschland",
        "category": ProgramCategory.ARBEIT,
        "level": ProgramLevel.ADVANCED,
        "short_description": "Move to Germany as a skilled worker under the Fachkräfteeinwanderungsgesetz.",
        "description": (
            "Germany actively recruits skilled workers (Fachkräfte) from outside the EU. "
            "The Skilled Immigration Act 2023 makes foreign qualification recognition faster "
            "and work-visa processing more straightforward. Salaries start around 2 500 €/month."
        ),
        "duration_months": None,
        "min_age": 18,
        "max_age": None,
        "language_requirement": "B1/B2",
        "salary_range": "2 500 – 5 000+ €/month",
        "is_published": True,
    },
    {
        "slug": "schule-exchange-year",
        "title": "Schuljahr in Deutschland",
        "category": ProgramCategory.SCHULE,
        "level": ProgramLevel.BEGINNER,
        "short_description": "Complete a full school year at a German Gymnasium and earn official credit.",
        "description": (
            "Spend one academic year at a German state school (Gymnasium) as an exchange student. "
            "You will live with a host family, attend regular classes, and gain a real feel for "
            "German culture and language. Programs run August/September to June."
        ),
        "duration_months": 10,
        "min_age": 14,
        "max_age": 18,
        "language_requirement": "A2/B1",
        "salary_range": "Exchange program fee varies",
        "is_published": True,
    },
]


# ── Seed runner ───────────────────────────────────────────────────────────────

async def seed() -> None:
    log.info("Creating database tables…")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # ── Admin user ────────────────────────────────────────────────────
        existing_admin = (
            await db.execute(select(User).where(User.email == "admin@WorldBridge.com"))
        ).scalar_one_or_none()

        if not existing_admin:
            admin = User(
                email="admin@WorldBridge.com",
                full_name="WorldBridge Admin",
                hashed_password=hash_password("Admin1234!"),
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            await db.flush()
            log.info("✅  Created admin user: admin@WorldBridge.com / Admin1234!")
        else:
            log.info("ℹ️  Admin user already exists, skipping.")

        # ── Sample programs ───────────────────────────────────────────────
        for prog_data in SAMPLE_PROGRAMS:
            exists = (
                await db.execute(select(Program).where(Program.slug == prog_data["slug"]))
            ).scalar_one_or_none()
            if not exists:
                db.add(Program(**prog_data))
                log.info(f"✅  Created program: {prog_data['title']}")
            else:
                log.info(f"ℹ️  Program '{prog_data['slug']}' already exists, skipping.")

        await db.commit()

    log.info("🎉  Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
