# stripe_payment_provider.py

import os
from typing import Dict, Optional

import stripe

from .base import PaymentProvider

# Initialize Stripe with your API key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class StripePaymentProvider(PaymentProvider):
    async def create_payment_session(
        self,
        amount: int,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """Creates a payment session using Stripe's API."""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "product_data": {
                                "name": "Product Name",
                            },
                            "unit_amount": amount,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=os.getenv("STRIPE_SUCCESS_URL"),
                cancel_url=os.getenv("STRIPE_CANCEL_URL"),
                metadata=metadata or {},
            )
            return {
                "session_id": session.id,
                "url": session.url,
            }
        except Exception as e:
            print(f"Error creating payment session: {e}")
            raise

    async def verify_payment(self, session_id: str) -> bool:
        """Verifies if the payment was successful for a given session."""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status == "paid"
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return False
