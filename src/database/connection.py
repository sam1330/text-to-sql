import os
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv

load_dotenv(override=True)

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Fallback to local sqlite for testing if no URL provided
        db_url = "sqlite:///insight_stream.db"
    
    engine = create_engine(db_url)
    db = SQLDatabase(engine)
    return db
