import streamlit as st
import pandas as pd
import plotly.express as px
from src.agent.router import SemanticRouter
from src.agent.sql_agent import InsightSQLAgent
from src.agent.explainer import ExplainerAgent
from src.viz.chart_agent import ChartAgent
from src.security.sanitizer import SQLSanitizer
from src.database.connection import get_db_connection
from sqlalchemy import text

# Page Configuration
st.set_page_config(
    page_title="InsightStream - Agentic Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #161b22;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 InsightStream")
st.subheader("Agentic Natural Language Analytics Pipeline")

# Initialize Agents
@st.cache_resource
def init_agents():
    return {
        "router": SemanticRouter(),
        "sql_agent": InsightSQLAgent(),
        "explainer": ExplainerAgent(),
        "chart_agent": ChartAgent(),
        "sanitizer": SQLSanitizer()
    }

agents = init_agents()

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.info("This agent uses a self-correction loop and security guardrails to ensure safe and accurate SQL generation.")
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# User Input
user_question = st.text_input("Ask a question about your data:", placeholder="e.g., Who are my top 5 customers by revenue?")

if user_question:
    with st.spinner("Analyzing your request..."):
        # 1. Routing
        route = agents["router"].route(user_question)
        
        if route == "general_llm":
            st.write("### 🤖 Response")
            # Using the router's llm which is now ChatGoogleGenerativeAI
            st.write(agents["router"].llm.invoke(user_question).content)
        else:
            # 2. SQL Generation & Safety
            st.write("### 🔍 System Logic")
            
            # Get the agent output (this is a bit tricky since we want the SQL before execution for explainability)
            # In a real LangChain agent, we'd use a callback or extract the SQL from the intermediate steps.
            # For this MVP, we'll run it and extract the SQL or rely on the agent's full response.
            
            try:
                response = agents["sql_agent"].run_query(user_question)
                # Note: LangChain SQL Agent usually returns the final answer. 
                # To show the SQL, we'd need to intercept the tool call.
                
                output = response.get("output", "No response.")
                
                # Show Explainability (Mocking the SQL extraction for now)
                explanation = agents["explainer"].explain("The generated SQL query", user_question)
                st.info(f"**Explanation:** {explanation}")
                
                st.write("### 📈 Results")
                st.success(output)
                
                # 3. Data Visualization
                # We'll Query the DB directly for the last result to show a table/chart
                db = get_db_connection()
                # For manual visualization, we'd need to store the last SQL.
                # Since we don't have it easily from the high-level agent call without callbacks, 
                # we will encourage the user to see the text response or implement a custom tool.
                
                st.warning("Note: Visual charts are generated based on the data summary provided by the agent.")
                chart_decision = agents["chart_agent"].select_chart(user_question, output)
                st.write(f"**Visualization Strategy:** {chart_decision.explanation}")
                st.write(f"**Selected Chart Type:** {chart_decision.chart_type}")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.divider()
st.caption("Powered by LangChain, GPT-4o, and Streamlit.")
