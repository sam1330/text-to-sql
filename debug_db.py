import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def debug_connection():
    db_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to: {db_url}")
    
    if not db_url:
        print("DATABASE_URL not found in environment.")
        return

    try:
        # Try direct psycopg2 connection first for better error messages
        print("Attempting direct psycopg2 connection...")
        conn = psycopg2.connect(db_url)
        print("✅ Direct psycopg2 connection successful!")
        conn.close()
    except Exception as e:
        print(f"❌ Direct psycopg2 connection failed: {e}")

    try:
        # Try SQLAlchemy connection
        print("\nAttempting SQLAlchemy connection...")
        engine = create_engine(db_url)
        with engine.connect() as connection:
            print("✅ SQLAlchemy connection successful!")
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")

if __name__ == "__main__":
    debug_connection()
