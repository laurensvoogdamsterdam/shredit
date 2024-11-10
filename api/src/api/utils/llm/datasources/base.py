from abc import ABC, abstractmethod
from typing import Any, List, Dict
from dataclasses import dataclass
from api.utils.llm.config import Config


# create Schema dataclass with tostr method


@dataclass
class TableSchema:
    table_name: str
    columns: List[Dict[str, str]]

    def __str__(self):
        return f"Table Name: {self.table_name}\n" + "\n".join(
            [f"- {column['name']} ({column['type']})" for column in self.columns]
        )


@dataclass
class Schema:
    tables: List[TableSchema]

    def __str__(self):
        return "Schema:" + "\n\n".join([str(table) for table in self.tables])


class DataSource(ABC):
    def __init__(self, config: Config):
        self.config = config
        self.connection = None  # Placeholder for database connection instance

    @abstractmethod
    @abstractmethod
    def validate_config(connection_string: str) -> bool:
        """Validates the configuration for the data source.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        """Connects to the database.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Executes a query on the database.

        Args:
            query (str): _description_
            params (Dict[str, Any], optional): _description_. Defaults to None.

        Returns:
            Any: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def get_schema(self) -> List[Dict[str, Any]]:
        """Gets the schema for a table.

        Returns:
            List[Dict[str, Any]]: _description_
        """
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnects from the database.

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
