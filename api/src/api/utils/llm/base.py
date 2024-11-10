from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Message:
    """
    Represents a single message in a conversation.
    """

    role: str  # only can be user or agent
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChatHistory:
    """
    Manages a collection of messages to maintain the conversation history.
    """

    messages: List[Message] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        """Adds a new message to the chat history.

        Args:
            role (str): _description_
            content (str): _description_
        """
        message = Message(role=role, content=content)
        self.messages.append(message)

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Returns the most recent messages in the chat history.

        Args:
            limit (int, optional): _description_. Defaults to 10.

        Returns:
            List[Message]: _description_
        """
        return self.messages[-limit:]

    def clear_history(self) -> None:
        """Clears the chat history."""
        self.messages.clear()


class BaseLLMAgent(ABC):
    """Base class for implementing a Language Model Agent.

    Args:
        ABC (_type_): _description_
    """

    def __init__(self):
        self.chat_history = ChatHistory()

    @abstractmethod
    def load_model(self, model_name: str, **kwargs: Dict[str, Any]) -> None:
        """Loads the language model.

        Args:
            model_name (str): _description_
        """
        raise NotImplementedError

    @abstractmethod
    def preprocess_input(self, user_input: str) -> str:
        """Preprocesses the user input before passing it to the model.

        Args:
            user_input (str): _description_

        Returns:
            str: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, processed_input: str, **kwargs: Dict[str, Any]) -> str:
        """Generates a response based on the processed input.

        Args:
            processed_input (str): _description_

        Returns:
            str: _description_
        """
        raise NotImplementedError

    def handle_context(self, user_input: str, response: str) -> None:
        """Handles the conversation context by adding the user input and response to the chat history.

        Args:
            user_input (str): _description_
            response (str): _description_
        """
        self.chat_history.add_message(role="user", content=user_input)
        self.chat_history.add_message(role="assistant", content=response)

    def reset_context(self) -> None:
        """Resets the conversation context by clearing the chat history."""
        self.chat_history.clear_history()

    def get_chat_history(self, limit: int = 10) -> List[Message]:
        """Returns the most recent messages in the chat history.

        Args:
            limit (int, optional): _description_. Defaults to 10.

        Returns:
            List[Message]: _description_
        """
        return self.chat_history.get_recent_messages(limit)
