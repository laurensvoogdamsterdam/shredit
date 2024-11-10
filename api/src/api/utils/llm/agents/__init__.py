

# create AgentFactory class
from .base import AgentFlow
from .main_agent import MainAgent

# class AgentFactory:
class AgentFactory:
    
    @staticmethod
    def build(agent_name: str = "main") -> AgentFlow:
        
        match agent_name:
            case "main":
                return MainAgent()
            
            case _:
                raise ValueError(f"Unknown agent: {agent_name}")
            


def get_agent(agent_name: str = "main") -> AgentFlow:
    return AgentFactory.build(agent_name)            