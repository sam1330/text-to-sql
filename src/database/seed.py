from src.database.connection import get_db_connection
from sqlalchemy import text

def seed_database():
    db = get_db_connection()
    with db._engine.connect() as conn:
        # Create tables
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id SERIAL PRIMARY KEY,
                name TEXT,
                attr_1 TEXT, -- subscription_status
                region TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name TEXT,
                price REAL,
                category TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER,
                amount REAL,
                status TEXT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
        """))
        
        # Insert sample data if empty
        result = conn.execute(text("SELECT COUNT(*) FROM customers"))
        if result.scalar() == 0:
            conn.execute(text("INSERT INTO customers (name, attr_1, region) VALUES ('Alice Smith', 'active', 'North America')"))
            conn.execute(text("INSERT INTO customers (name, attr_1, region) VALUES ('Bob Jones', 'pended', 'Europe')"))
            conn.execute(text("INSERT INTO customers (name, attr_1, region) VALUES ('Charlie Brown', 'active', 'Europe')"))
            
            conn.execute(text("INSERT INTO products (name, price, category) VALUES ('Laptop', 1200.0, 'Electronics')"))
            conn.execute(text("INSERT INTO products (name, price, category) VALUES ('Mouse', 25.0, 'Electronics')"))
            
            conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (1, 1225.0, 'shipped')"))
            conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (2, 25.0, 'processing')"))
            conn.execute(text("INSERT INTO orders (customer_id, amount, status) VALUES (3, 0.0, 'cancelled')"))
            
            conn.commit()
            print("Database seeded successfully.")
        else:
            print("Database already contains data.")

if __name__ == "__main__":
    seed_database()
