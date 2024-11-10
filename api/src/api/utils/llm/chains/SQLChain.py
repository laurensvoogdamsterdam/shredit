import os
import logging
from sqlalchemy import create_engine, inspect
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from tabulate import tabulate
from api.utils.llm.prompts.sql_generation import prompt as sql_generation_prompt
from api.utils.llm.prompts.sql_based_response import prompt as sql_based_response_prompt
from typing import Any, Dict
from api.utils.llm.config import Config
from api.utils.llm.datasources import DataSourceFactory
from api.utils.logger import log


class SQLChain:

    def __init__(self, config: Config):
        self.config = config
        self.generate_query_chain = (
            sql_generation_prompt()
            | ChatOpenAI(
                model=config.llm.model_name, max_retries=config.llm.max_retries
            )
            | StrOutputParser()
        )
        self.generate_response_chain = (
            sql_based_response_prompt
            | ChatOpenAI(
                model=config.llm.model_name, max_retries=config.llm.max_retries
            )
            | StrOutputParser()
        )

    def execute_query(self, query: str, db: SQLDatabase) -> str:
        try:
            with DataSourceFactory.build(self.config) as datasource:
                result = datasource.execute(query)
                if result is None:
                    return "Query executed successfully."
                else:
                    return tabulate(result, headers="keys", tablefmt="pretty")
        except Exception as e:
            log.error(f"Error executing query: {e}")
            return f"Error executing query: {e}"

    def get_schema(self) -> str:
        try:
            schema = self.datasource.get_schema()
            return str(schema)
        except Exception as e:
            log.error(f"Error getting schema: {e}")
            return f"Error getting schema: {e}"

    def run(self, data: Dict[str, Any]) -> str:
        """Runs the SQL chain.

        Args:
            data (Dict[str, Any]): _description_

        Returns:
            str: _description_
        """
        schema = self.get_schema()
        query = self.generate_query_chain.run(
            {"schema": schema, "question": data["question"]}
        )
        query_response = self.execute_query(query)
        response = self.generate_response_chain.run(
            {
                "schema": schema,
                "question": data["question"],
                "query": query,
                "response": query_response,
            }
        )
        return response
