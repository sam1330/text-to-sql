import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class ChartSelection(BaseModel):
    """Select the best chart type for the data."""
    chart_type: str = Field(
        ...,
        description="Type of chart to generate: 'bar', 'line', 'pie', 'table', or 'none'.",
    )
    explanation: str = Field(..., description="Reason for choosing this chart type.")

class ChartAgent:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.structured_llm = self.llm.with_structured_output(ChartSelection)
        
        system = """You are a visualization expert. Given a user question and the data results (summary), 
        decide which chart type is most appropriate to display the information.
        Options: 'bar' (categories), 'line' (trends over time), 'pie' (parts of a whole), 'table' (raw data), or 'none' (text only)."""
        
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Question: {question}\nData Preview: {data}"),
            ]
        )
        self.chain = self.prompt | self.structured_llm

    def select_chart(self, question: str, data_summary: str):
        return self.chain.invoke({"question": question, "data": data_summary})
