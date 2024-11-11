from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    """You are good at classifying a question.
    Given the user question below, classify it as either being about `Database`, `Chat`, or 'Offtopic'.

    <If the question is about products of the restaurant OR ordering food, drinks and anything related to the products of a restaurant, classify the question as 'database'>
    <If the question is about restaurant-related topics like opening hours and similar topics, classify the question as 'chat'>
    <If the question is about weather, football, or anything not related to the restaurant or products, classify the question as 'offtopic'>

    Question: {question}

    Chat history: {history}

    classification: """
)