"""
CalculatorService — pure business logic for the relocation cost estimator.
No I/O: takes a CalculatorInput and returns a CalculatorResult synchronously.
"""

from schemas.calculator import CalculatorInput, CalculatorResult

# City-specific rent multipliers (compared to national average baseline)
_CITY_MULTIPLIERS: dict[str, float] = {
    "münchen": 1.55,
    "munich": 1.55,
    "frankfurt": 1.35,
    "hamburg": 1.25,
    "berlin": 1.10,
    "köln": 1.05,
    "cologne": 1.05,
    "düsseldorf": 1.15,
    "stuttgart": 1.20,
    "leipzig": 0.85,
    "dresden": 0.80,
    "default": 1.00,
}

# Utility estimate if not included in rent (EUR/month, per person)
_UTILITIES_PER_PERSON = 80.0

# Kindergarten / childcare estimate per child
_CHILDCARE_PER_CHILD = 300.0


class CalculatorService:

    @staticmethod
    def calculate(data: CalculatorInput) -> CalculatorResult:
        city_key = data.city.lower().strip()
        multiplier = _CITY_MULTIPLIERS.get(city_key, _CITY_MULTIPLIERS["default"])

        # ── One-time costs ────────────────────────────────────────────────────
        visa_docs = data.visa_fee + data.document_legalisation_cost
        flight_total = data.flight_cost * data.family_members
        one_time_total = visa_docs + flight_total

        # ── Monthly costs ─────────────────────────────────────────────────────
        # Housing: apply city multiplier; add utility estimate if not included
        housing = data.monthly_rent * multiplier
        if not data.utilities_included:
            housing += _UTILITIES_PER_PERSON * data.family_members
        if data.has_children:
            housing += _CHILDCARE_PER_CHILD  # rough childcare/school estimate

        lang_monthly = (
            data.language_course_price_per_month
            if data.language_course_months > 0
            else 0.0
        )
        misc = data.misc_monthly * data.family_members
        monthly_total = (
            housing
            + lang_monthly
            + data.health_insurance_monthly
            + misc
        )

        # ── Course & buffer totals ────────────────────────────────────────────
        lang_total = data.language_course_price_per_month * data.language_course_months
        savings_buffer = monthly_total * data.months_of_savings
        grand_total = one_time_total + lang_total + savings_buffer

        # ── Tips ─────────────────────────────────────────────────────────────
        tips = CalculatorService._generate_tips(data, city_key, multiplier)

        return CalculatorResult(
            visa_and_documents=round(visa_docs, 2),
            flight_total=round(flight_total, 2),
            one_time_total=round(one_time_total, 2),
            housing_monthly=round(housing, 2),
            language_course_monthly=round(lang_monthly, 2),
            health_insurance_monthly=round(data.health_insurance_monthly, 2),
            misc_monthly=round(misc, 2),
            monthly_total=round(monthly_total, 2),
            language_course_total=round(lang_total, 2),
            savings_buffer=round(savings_buffer, 2),
            grand_total=round(grand_total, 2),
            tips=tips,
            city=data.city,
        )

    @staticmethod
    def _generate_tips(
        data: CalculatorInput, city_key: str, multiplier: float
    ) -> list[str]:
        tips: list[str] = []

        if multiplier > 1.3:
            tips.append(
                f"{data.city} is one of Germany's most expensive cities. "
                "Consider nearby suburbs to reduce rent by 20–30 %."
            )
        if data.language_course_months == 0:
            tips.append(
                "Even a basic German course (A1–A2) significantly improves "
                "your daily life and job prospects in Germany."
            )
        if data.months_of_savings < 3:
            tips.append(
                "Financial advisors recommend at least 3 months of living "
                "expenses as an emergency buffer when relocating abroad."
            )
        if not data.utilities_included:
            tips.append(
                "Try to negotiate Warmmiete (rent with utilities included) "
                "to simplify budgeting and avoid surprise bills."
            )
        if data.family_members > 1:
            tips.append(
                "Look into family-based Wohngeld (housing benefit) — you "
                "may qualify for a state subsidy depending on income."
            )
        if data.has_children:
            tips.append(
                "Register for Kindergeld (child benefit) as soon as you "
                "arrive — it's up to 250 € / month per child."
            )

        if not tips:
            tips.append(
                "Great planning! Open a German bank account (e.g. N26 or DKB) "
                "before arrival to receive your first salary without delays."
            )

        return tips
