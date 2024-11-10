#  create abstract base class for AgentFlow

from abc import ABC, abstractmethod
from typing import Any, Dict
from api.utils.llm.config import Message   


class AgentFlow(ABC):
    @abstractmethod
    async def run(self, data: Dict[str, Any]) -> Message:
        """Runs the agent

        Args:
            data (Dict[str, Any]): _description_

        Returns:
            Message: _description_
        """
        raise NotImplementedError
