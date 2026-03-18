# Project: InsightStream – Agentic Natural Language Analytics Pipeline

## 🎯 Overview
InsightStream is a "Text-to-SQL" system that translates natural language questions into complex SQL queries, executes them safely, and returns both a visual chart and a natural language summary. It includes a **Self-Correction Loop** (to fix syntax errors) and an **Explainability Layer** (to show the user the logic before running the query).

## 🛠 Tech Stack
* **Orchestration:** LangChain (SQL Agent) or LlamaIndex.
* **LLM:** GPT-4o (High reasoning for SQL generation).
* **Database:** PostgreSQL (with a sample dataset like Northwind or a custom SaaS schema).
* **Metadata Management:** Schema-level descriptions stored in a YAML file or Vector DB.
* **Frontend:** Streamlit or Vercel v0 (for instant data visualization).
* **Safety:** SQLGlot (for query transpilation and sanitization).

---

## 🏗 System Architecture



### The Workflow Logic:
1.  **Semantic Router:** The agent determines if the query is a "Data Query" (SQL) or a "General Question" (General LLM).
2.  **Schema Pruning:** Instead of sending the *entire* database schema to the LLM (which is expensive and confusing), the system uses a Vector DB to retrieve only the relevant table definitions.
3.  **SQL Generation:** The LLM generates the SQL based on the pruned schema and specific business rules (e.g., "Active users are defined as those who logged in within 30 days").
4.  **The "Check-Engine" Loop:** * The SQL is run against a "Dry Run" validator.
    * If the database returns an error, the error message is fed back to the LLM to rewrite the query.
5.  **Data-to-Viz:** The resulting JSON/Dataframe is sent to a specialized "Chart Agent" that decides if a Bar, Line, or Pie chart is most appropriate.
6.  **Privacy Masking:** PII (Personally Identifiable Information) is automatically scrubbed from the final output.

---

## 🚀 Step-by-Step Implementation

### Phase 1: Knowledge Augmentation (The Context)
* **Task:** Create a `dictionary.yaml` that defines what column names actually mean.
* **Example:** `attr_1` might mean `subscription_status`. The LLM needs this mapping to be accurate.

### Phase 2: The SQL Agent (LangChain)
* **Task:** Initialize the `SQLDatabaseChain`.
* **Feature:** Implement "Few-Shot Prompting." Give the LLM 5 examples of complex joins relevant to your specific data so it learns your "style."

### Phase 3: The Self-Healing Loop
* **Task:** Wrap the execution in a `try-except` block.
* **Logic:**
    ```python
    if "column does not exist" in db_error:
        prompt_llm("The previous query failed with this error: {db_error}. Please check the schema and try again.")
    ```

### Phase 4: Visualization & Explainability
* **Task:** Before showing data, the agent must output: *"I am calculating this by joining the 'Orders' and 'Customers' tables, filtering for the 'Europe' region, and summing the 'Total' column."*
