# InsightStream – Agentic Natural Language Analytics Pipeline

## 🎯 Overview
InsightStream is a "Text-to-SQL" system that translates natural language questions into SQL, executes them safely, and returns both a chart and a natural-language answer. It routes each question to either a SQL agent or a general LLM, explains the SQL logic in plain English before showing results, and retries failed queries by feeding the database error back to the LLM.

## 🛠 Tech Stack
* **Orchestration:** LangChain (`create_sql_agent` with tool-calling)
* **LLM:** Google Gemini (`gemini-2.5-flash` by default, via `langchain-google-genai`)
* **Database:** PostgreSQL (falls back to local SQLite if `DATABASE_URL` is unset)
* **Metadata:** Table/column descriptions in [data/dictionary.yaml](data/dictionary.yaml)
* **Frontend:** Streamlit ([app.py](app.py))
* **Visualization:** Plotly Express, chart type/code chosen by an LLM agent
* **Safety:** `sqlparse`-based keyword blocklist + auto `LIMIT` injection ([src/security/sanitizer.py](src/security/sanitizer.py))

## 🏗 Architecture

```
User question
    │
    ▼
SemanticRouter ──▶ general_llm (plain chat answer)
    │
    ▼ sql_agent
InsightSQLAgent (LangChain SQL agent + dictionary.yaml context + few-shot examples)
    │  self-correction loop: re-prompts with the DB error on failure, up to 3 attempts
    ▼
ExplainerAgent ──▶ plain-English explanation of the generated SQL
    │
    ▼
DataFrame fetched via SQLAlchemy
    │
    ▼
ChartAgent ──▶ picks chart type (bar/line/pie/table/none) + generates Plotly code
    │
    ▼
Streamlit UI: explanation, data table, chart
```

### Components
| Module | Responsibility |
|---|---|
| [src/agent/router.py](src/agent/router.py) | Routes a question to `sql_agent` or `general_llm` using structured output |
| [src/agent/sql_agent.py](src/agent/sql_agent.py) | Runs the LangChain SQL agent with dictionary context + few-shot prompt, retries on error |
| [src/agent/explainer.py](src/agent/explainer.py) | Turns the generated SQL into a natural-language explanation |
| [src/viz/chart_agent.py](src/viz/chart_agent.py) | Chooses a chart type and generates one line of Plotly Express code |
| [src/database/connection.py](src/database/connection.py) | Builds the SQLAlchemy/`SQLDatabase` connection (Postgres or SQLite fallback) |
| [src/database/metadata.py](src/database/metadata.py) | Loads `data/dictionary.yaml` and formats it as LLM context |
| [src/database/pruner.py](src/database/pruner.py) | Chroma-backed vector search to retrieve only relevant tables for a question |
| [src/database/seed.py](src/database/seed.py) | Creates and seeds `customers`, `products`, `orders` sample tables |
| [src/security/sanitizer.py](src/security/sanitizer.py) | Blocks destructive SQL keywords and enforces a `LIMIT` |

> Note: `SchemaPruner` (vector-based schema retrieval) exists but isn't wired into the app flow yet — `InsightSQLAgent` currently sends the full dictionary context on every request.

## 🚀 Getting Started

### 1. Configure environment
```bash
cp .env.example .env
# then fill in GOOGLE_API_KEY, MODEL_NAME, DATABASE_URL
```

### 2. Run with Docker (Postgres + app)
```bash
docker-compose up --build
```
The app will be available at `http://localhost:8501`. On first run, seed the sample data:
```bash
python -m src.database.seed
```

### 3. Run locally
```bash
pip install -r requirements.txt
python -m src.database.seed   # optional: seeds sample customers/products/orders
streamlit run app.py
```
Without a `DATABASE_URL`, the app falls back to a local `insight_stream.db` SQLite file.

## 📁 Sample Schema
Seeded via [src/database/seed.py](src/database/seed.py):
* **customers** — `id, name, attr_1 (subscription status), region, created_at`
* **products** — `id, name, price, category`
* **orders** — `id, customer_id, product_id, amount, status, order_date`

Column meanings for the LLM are documented in [data/dictionary.yaml](data/dictionary.yaml).
