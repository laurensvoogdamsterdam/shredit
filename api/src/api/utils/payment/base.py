# payment_provider.py

from abc import ABC, abstractmethod
from typing import Dict, Optional


class PaymentProvider(ABC):
    @abstractmethod
    async def create_payment_session(
        self, amount: int, currency: str, metadata: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Creates a payment session and returns session details."""
        pass

    @abstractmethod
    async def verify_payment(self, session_id: str) -> bool:
        """Verifies the payment status for a given session ID."""
        pass
