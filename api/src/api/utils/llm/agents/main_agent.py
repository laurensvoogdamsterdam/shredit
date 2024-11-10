from .base import AgentFlow
from typing import List
from api.utils.llm.config import Message
from langchain_openai import ChatOpenAI



class MainAgent(AgentFlow):
    """_description_

    Args:
        AgentFlow (_type_): _description_
    """
    def __init__(self):
        pass

    async def run(self, question: str, history: List[Message]) -> Message:
        """ Run agent flow

        Args:
            question (str): _description_

        Returns:
            Message: _description_
        """
        model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
        # get answer from model.invoke(question)
        response = model.invoke(question)
        # get content from  response
        answer = response.content
        
        return Message(
            role="agent",
            content=answer
        )