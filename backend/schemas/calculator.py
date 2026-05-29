from typing import Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Input
# ─────────────────────────────────────────────────────────────────────────────

class CalculatorInput(BaseModel):
    """
    Parameters supplied by the user for the relocation cost estimator.

    All monetary fields are in EUR.  Provide only the fields relevant
    to the selected program — optional fields default to 0 / None.
    """

    # ── Destination ──────────────────────────────────────────────────────
    city: str = Field(..., examples=["Berlin"], description="Target German city")

    # ── Personal situation ────────────────────────────────────────────────
    family_members: int = Field(1, ge=1, le=10, description="Total people relocating (incl. yourself)")
    has_children: bool = Field(False, description="Whether any children are relocating")

    # ── Housing ──────────────────────────────────────────────────────────
    monthly_rent: float = Field(..., ge=0, description="Expected monthly rent (EUR)")
    utilities_included: bool = Field(False, description="Are utilities included in rent?")

    # ── Language courses ──────────────────────────────────────────────────
    language_course_months: int = Field(0, ge=0, le=24, description="Number of months of German course needed")
    language_course_price_per_month: float = Field(200.0, ge=0, description="Cost per month of language course (EUR)")

    # ── Visa & documents ──────────────────────────────────────────────────
    visa_fee: float = Field(75.0, ge=0, description="National-visa application fee (EUR)")
    document_legalisation_cost: float = Field(0.0, ge=0, description="Apostille / notary costs (EUR)")

    # ── Travel ────────────────────────────────────────────────────────────
    flight_cost: float = Field(0.0, ge=0, description="One-way flight cost per person (EUR)")

    # ── Savings / buffer ─────────────────────────────────────────────────
    months_of_savings: int = Field(3, ge=1, le=12, description="How many months of buffer to plan for")

    # ── Optional extra costs ──────────────────────────────────────────────
    health_insurance_monthly: float = Field(0.0, ge=0, description="Monthly private health insurance if not covered")
    misc_monthly: float = Field(300.0, ge=0, description="Miscellaneous living costs per month (food, transport, etc.)")


# ─────────────────────────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────────────────────────

class CalculatorResult(BaseModel):
    """Detailed cost breakdown returned by the calculator."""

    # ── One-time costs ────────────────────────────────────────────────────
    visa_and_documents: float
    flight_total: float
    one_time_total: float

    # ── Monthly costs ─────────────────────────────────────────────────────
    housing_monthly: float          # rent + utilities estimate
    language_course_monthly: float
    health_insurance_monthly: float
    misc_monthly: float
    monthly_total: float

    # ── Totals ────────────────────────────────────────────────────────────
    language_course_total: float    # full course duration
    savings_buffer: float           # monthly_total × months_of_savings
    grand_total: float              # one_time + language_course + savings_buffer

    # ── Tips ─────────────────────────────────────────────────────────────
    tips: list[str] = Field(default_factory=list)
    city: str
