# main.py or your FastAPI route file

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

import api.db.models as models
from api.db.pool import get_db
from api.utils.payment import PaymentProvider, PaymetProviderFactory

router = APIRouter(
    prefix="/payment",
    tags=["payment"],
)


@router.post("/create")
async def create_payment_session(
    amount: int,
    request: Request,
    currency: str = "eur",
    db: AsyncSession = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_db),
):
    """Create a payment session for a given amount and currency.

    Args:
        amount (int): _description_
        request (Request): _description_
        currency (str, optional): _description_. Defaults to "eur".
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        payment_provider (PaymetProviderFactory, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        session = await payment_provider.create_payment_session(amount, currency)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create payment session.")


@router.get("/verify-payment/{session_id}")
async def verify_payment(
    session_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    payment_provider: PaymentProvider = Depends(get_db),
):
    """Verify the payment status for a given session ID.

    Args:
        session_id (str): _description_
        request (Request): _description_
        db (AsyncSession, optional): _description_. Defaults to Depends(get_db).
        payment_provider (PaymetProviderFactory, optional): _description_. Defaults to Depends(get_db).

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    try:
        payment_successful = await payment_provider.verify_payment(session_id)
        return {"success": payment_successful}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to verify payment.")
