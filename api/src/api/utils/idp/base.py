from abc import ABC, abstractmethod

from fastapi import HTTPException, Request


class IdentityProvider(ABC):
    @abstractmethod
    async def validate_token(self, token: str) -> dict:
        """Validate the token with the identity

        Args:
            token (str): _description_

        Returns:
            dict: _description_
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_info(self, token: str) -> dict:
        """Get user info from the token.

        Args:
            token (str): _description_

        Returns:
            dict: _description_
        """
        raise NotImplementedError
