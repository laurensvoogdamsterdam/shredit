import os
from typing import Any, Dict

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from api.utils.llm.prompts.classification import prompt

from api.utils.llm.router.base import BaseRouter


class ClassificationRouter(BaseRouter):
    """
    Routes questions based on their classification using an LLM-powered classification chain.
    """

    def __init__(self):
        self.chain = (
            prompt
            | ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), max_retries=5)
            | StrOutputParser()
        )

    def route(self, question: str) -> str:
        """Routes the incoming question to the appropriate LLM agent.

        Args:
            question (str): _description_

        Returns:
            str: _description_
        """
        return self.chain.run({"question": question})
