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
    # 1. Routing
    with st.status("Analyzing your request...") as status:
        status.write("🚦 Routing request...")
        route = agents["router"].route(user_question)
        
        if route == "general_llm":
            status.update(label="🤖 General Response", state="complete")
            st.write("### 🤖 Response")
            st.write(agents["router"].llm.invoke(user_question).content)
        else:
            status.write("🔍 Generating SQL & Checking Schema...")
            try:
                response = agents["sql_agent"].run_query(user_question)
                output = response.get("output", "No response.")
                sql_query = response.get("sql")
                
                if sql_query:
                    status.write("📝 Explaining logic...")
                    explanation = agents["explainer"].explain(sql_query, user_question)
                    st.info(f"**Explanation:** {explanation}")
                
                status.write("📊 Fetching data & Creating visualization...")
                
                st.write("### 📈 Results")
                st.success(output)
                
                # 3. Data Visualization
                if sql_query:
                    try:
                        engine = agents["sql_agent"].db._engine
                        df = pd.read_sql(sql_query, engine)
                        
                        if not df.empty:
                            st.dataframe(df, width="stretch")
                            
                            chart_decision = agents["chart_agent"].select_chart(user_question, output)
                            
                            if chart_decision.chart_type not in ["none", "table"]:
                                st.info(f"**Visualization Strategy:** {chart_decision.explanation}")
                                
                                chart_code = agents["chart_agent"].generate_plotly_code(
                                    user_question, 
                                    df.columns.tolist(), 
                                    chart_decision.chart_type
                                )
                                
                                try:
                                    local_vars = {"df": df, "px": px}
                                    exec(f"fig = {chart_code}", {}, local_vars)
                                    fig = local_vars.get("fig")
                                    if fig:
                                        st.plotly_chart(fig, width="stretch")
                                except Exception as viz_e:
                                    st.warning(f"Could not generate chart: {viz_e}")
                            else:
                                st.write("Table visualization selected for this data.")
                        else:
                            st.info("The query returned no data to visualize.")
                    except Exception as db_e:
                        st.error(f"Error retrieving data for visualization: {db_e}")
                else:
                    st.warning("No SQL query could be extracted for visualization.")
                
                status.update(label="✅ Analysis Complete", state="complete")

            except Exception as e:
                status.update(label="❌ Error Occurred", state="error")
                st.error(f"An error occurred: {str(e)}")

# Footer
st.divider()
st.caption("Powered by LangChain, Gemini AI, and Streamlit.")
