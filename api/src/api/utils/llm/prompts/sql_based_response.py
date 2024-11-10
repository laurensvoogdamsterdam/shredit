from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    """Based on the table schema below, question, SQL query, and SQL response, write a natural language response, without indicating that the data was retrieved from a database:
    {schema}

    Question: {question}
    SQL Query: {query}
    SQL Response: {response}
    """
)
