import os

from .base import PaymentProvider
from .stripe import StripePaymentProvider


class PaymetProviderFactory:
    @staticmethod
    def build() -> PaymentProvider:
        payment_provider = os.getenv("PAYMENT_PROVIDER", "stripe")
        match payment_provider:
            case "stripe":
                return StripePaymentProvider()
            case _:
                raise ValueError("Invalid payment provider")


def get_payment_provider() -> PaymentProvider:
    return PaymetProviderFactory.build()
