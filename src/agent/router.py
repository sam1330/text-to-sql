import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class RouteQuery(BaseModel):
    """Route a user query to the most appropriate datasource."""
    datasource: str = Field(
        ...,
        description="Given a user question choose to route it to sql_agent or general_llm.",
    )

class SemanticRouter:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.structured_llm_router = self.llm.with_structured_output(RouteQuery)
        
        system = """You are an expert at routing user queries to a SQL agent or a general LLM.
        The SQL agent has access to a database with customers, orders, and products.
        Use 'sql_agent' for questions about data, statistics, products, orders, or customers.
        Use 'general_llm' for greeting, general knowledge, or questions unrelated to the business data."""
        
        self.route_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "{question}"),
            ]
        )
        self.router = self.route_prompt | self.structured_llm_router

    def route(self, question: str) -> str:
        result = self.router.invoke({"question": question})
        return result.datasource
