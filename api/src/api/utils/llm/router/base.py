from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRouter(ABC):
    """
    Abstract base class for routing incoming questions to the appropriate LLM agent.
    """

    @abstractmethod
    def route(self, question: str) -> str:
        """Routes the incoming question to the appropriate LLM agent.

        Args:
            question (str): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            str: _description_
        """
        raise NotImplementedError
