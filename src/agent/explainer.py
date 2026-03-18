import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class ExplainerAgent:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        
        system = """You are an explainability agent for a Data Analytics system. 
        Your job is to translate a complex SQL query into a clear, natural language explanation 
        of what logic the system is about to run. 
        Focus on: what tables are joined, what filters are applied, and what is being calculated."""
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "SQL Query: {sql}\nUser Question: {question}"),
            ]
        )
        self.chain = self.prompt | self.llm

    def explain(self, sql: str, question: str):
        response = self.chain.invoke({"sql": sql, "question": question})
        return response.content
