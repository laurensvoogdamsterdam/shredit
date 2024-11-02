import os

from api.utils.idp.auth0 import Auth0IdentifyProvider
from api.utils.idp.base import IdentityProvider


class IdentifyProviderFactory:
    """Factory to create an IdentifyProvider instance."""

    @staticmethod
    def build() -> IdentityProvider:
        """Create an IdentifyProvider instance.

        Returns:
            IdentifyProvider: An IdentifyProvider instance.
        """
        auth_provider = os.getenv("AUTH_PROVIDER", "auth0")
        match auth_provider:
            case "auth0":
                return Auth0IdentifyProvider()
            case _:
                raise ValueError(f"Invalid AUTH_PROVIDER: {auth_provider}")
