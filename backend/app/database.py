import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Explicitly point to .env in backend folder
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return "Database connected successfully"
    except Exception as e:
        return f"Database connection failed: {str(e)}"
