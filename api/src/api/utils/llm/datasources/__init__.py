from .postgres import PostgresDataSource
from .base import DataSource, Config


class DataSourceFactory:

    @staticmethod
    def build(config: Config) -> DataSource:
        if config.database.type == "postgres":
            return PostgresDataSource(config)
        else:
            raise ValueError("Invalid datasource type")
