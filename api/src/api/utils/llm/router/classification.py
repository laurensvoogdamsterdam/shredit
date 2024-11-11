import os
from typing import Any, Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from enum import Enum
from dataclasses import dataclass
from api.utils.llm.prompts.classification import prompt
from api.utils.llm.config import Message

from api.utils.llm.router.base import BaseRouter

# Step 1: Define the Enum for Restricted Field Values
class Classification(str, Enum):
    CHAT = "chat"
    DATABASE = "database"
    OTHER = "other" 
    

# Step 2: Define the Output Dataclass with Enum Field
@dataclass
class StructuredResponse:
    classification: Classification
    


class ClassificationRouter(BaseRouter):
    """
    Routes questions based on their classification using an LLM-powered classification chain.
    """

    def __init__(self):
        self.chain = (
            prompt
            | ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), max_retries=5)
            .with_structured_output(StructuredResponse)
        )

    def route(self, question: str, history: List[Message] = []) -> StructuredResponse:
        """Routes the incoming question to the appropriate LLM agent.

        Args:
            question (str): _description_

        Returns:
            StructuredResponse: _description_
        """
        return StructuredResponse(**self.chain.invoke({"question": question, "history": history}))
