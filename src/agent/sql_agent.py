from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from src.database.connection import get_db_connection
from src.database.metadata import MetadataManager
import os

class InsightSQLAgent:
    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
        self.db = get_db_connection()
        self.metadata_mgr = MetadataManager()
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            agent_type="openai-functions",
        )

    def _get_few_shot_prompt(self):
        return """
        Few-shot examples for complex queries:
        1. "Who are my top 5 customers by revenue?"
           SQL: SELECT c.name, SUM(o.amount) as total_revenue FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id ORDER BY total_revenue DESC LIMIT 5;
        2. "Show active customers in Europe."
           SQL: SELECT name FROM customers WHERE attr_1 = 'active' AND region = 'Europe';
        3. "Total sales of Electronics products."
           SQL: SELECT SUM(o.amount) FROM orders o JOIN products p ON 1=1 WHERE p.category = 'Electronics'; -- (Simplification, real joins depend on schema)
        """

    def run_query(self, user_question: str, max_retries: int = 3):
        context = self.metadata_mgr.get_full_context()
        few_shot = self._get_few_shot_prompt()
        
        prompt = f"{context}\n\n{few_shot}\n\nUser Question: {user_question}"
        
        attempt = 0
        last_error = ""
        
        while attempt < max_retries:
            try:
                if last_error:
                    retry_prompt = f"The previous attempt failed with this error: {last_error}. Please correct the SQL and try again.\n\n{prompt}"
                    return self.agent_executor.invoke({"input": retry_prompt})
                else:
                    return self.agent_executor.invoke({"input": prompt})
            except Exception as e:
                last_error = str(e)
                print(f"Error on attempt {attempt + 1}: {last_error}")
                attempt += 1
        
        return {"output": f"Failed after {max_retries} attempts. Last error: {last_error}"}
