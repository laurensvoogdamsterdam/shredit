from api.utils.llm.datasources.base import DataSource, TableSchema, Schema
from typing import Any, Dict, List
from sqlalchemy import create_engine, inspect


class PostgresDataSource(DataSource):

    @staticmethod
    def validate_config(connection_string: str) -> bool:
        """Validate the connection string

        Args:
            connection_string (str): _description_

        Returns:
            bool: _description_
        """
        try:
            engine = create_engine(connection_string)
            connection = engine.connect()
            connection.close()
            return True
        except Exception as e:
            return False

    def connect(self) -> None:
        """Connect to the database"""
        engine = create_engine(self.config.database.connection_string())
        #  connect to db
        self.connection = engine.connect()

    def execute(self, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute a query

        Args:
            query (str): _description_
            params (Dict[str, Any], optional): _description_. Defaults to None.

        Returns:
            Any: _description_
        """
        with self.connection as conn:
            result = conn.execute(query, params)
            if result.returns_rows:
                return result.fetchall()
            else:
                return None

    def get_schema(self) -> List[Dict[str, Any]]:
        """Get the schema of the database

        Returns:
            List[Dict[str, Any]]: _description_
        """

        with self.connection as conn:
            inspector = inspect(conn)
            #  for each table, get the table schema
            tables = inspector.get_table_names()
            schema = []
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                schema.append(
                    TableSchema(
                        table_name=table_name,
                        columns=[
                            {"name": column["name"], "type": column["type"]}
                            for column in columns
                        ],
                    )
                )
            return Schema(tables=schema)

    def disconnect(self) -> None:
        """Disconnect from the database"""
        if self.connection:
            self.connection.close()
            self.connection = None
