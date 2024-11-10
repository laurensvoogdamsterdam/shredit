import os
from dataclasses import dataclass, fields
from typing import List


@dataclass
class DatabaseConfig:
    type: str
    user: str
    password: str
    host: str
    port: int
    db_name: str
    schema: str = None  # Only used for databases like Snowflake

    def __init__(
        self,
        type: str = None,
        user: str = None,
        password: str = None,
        host: str = None,
        port: int = None,
        db_name: str = None,
        schema: str = None,
    ):
        # Set values based on constructor arguments or environment variables as fallback
        self.type = type or os.getenv("DB_TYPE", "postgresql")
        self.user = user or os.getenv("DB_USER", "admin")
        self.password = password or os.getenv("DB_PASSWORD", "admin")
        self.host = host or os.getenv("DB_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("DB_PORT", 5432))
        self.db_name = db_name or os.getenv("DB_NAME", "vectordb")
        self.schema = schema or os.getenv(
            "DB_SCHEMA", "public"
        )  # Relevant for Snowflake

    def connection_string(self) -> str:
        if self.type == "postgresql":
            return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.type == "mysql":
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.type == "snowflake":
            # Snowflake requires the schema to be specified as part of the connection string
            return f"snowflake://{self.user}:{self.password}@{self.host}/{self.db_name}/{self.schema}"
        else:
            raise ValueError(f"Unsupported database type: {self.type}")


@dataclass
class LLMConfig:
    model_name: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "5"))


@dataclass
class Message:
    role: str
    content: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)
    
    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}    


@dataclass
class Chat:
    question: str
    history: List[Message]


@dataclass
class Config:
    database: DatabaseConfig = DatabaseConfig()
    llm: LLMConfig = LLMConfig()
    chat: Chat = Chat(question=str(None), history=[])
