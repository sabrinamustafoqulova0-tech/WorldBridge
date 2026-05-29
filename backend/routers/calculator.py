from fastapi import APIRouter, Depends

from schemas.calculator import CalculatorInput, CalculatorResult
from services.calculator_service import CalculatorService
from utils.dependencies import get_current_active_user

router = APIRouter(prefix="/calculator", tags=["Calculator"])


@router.post("", response_model=CalculatorResult)
async def calculate_relocation_costs(
    payload: CalculatorInput,
    _=Depends(get_current_active_user),
):
    """
    Calculate the estimated total cost of relocating to Germany.

    Requires authentication so results can optionally be saved in
    the future. Returns a detailed cost breakdown and money-saving tips.
    """
    return CalculatorService.calculate(payload)


@router.post("/preview", response_model=CalculatorResult)
async def calculate_preview(payload: CalculatorInput):
    """
    Public (unauthenticated) quick estimate — same logic, no saved history.
    """
    return CalculatorService.calculate(payload)
