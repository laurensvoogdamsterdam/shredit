from .base import AgentFlow
from api.utils.llm.config import Message


class MainAgent(AgentFlow):
    """_description_

    Args:
        AgentFlow (_type_): _description_
    """
    def __init__(self):
        pass

    async def run(self, question: str) -> Message:
        """ Run agent flow

        Args:
            question (str): _description_

        Returns:
            Message: _description_
        """
        return Message(
            role="agent",
            content="Hello, I am the main agent. How can I help you?"
        )