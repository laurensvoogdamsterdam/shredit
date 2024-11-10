from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    """Based on the table schema below, write a SQL query that would answer the user's question:
    {schema}

    Important: ONLY provide the query, nothing else.

    Example:
    Table Name: Customers
    Columns:
    - id (int)
    - name (varchar)
    - email (varchar)
    - created_at (date)

    Question: Show me all customer email addresses.
    SELECT email FROM Customers;

    Question: {question}
    SQL Query:"""
)
