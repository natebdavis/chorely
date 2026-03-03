import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import pathlib

# Load environment variables from .env file in root folder
load_dotenv(dotenv_path=pathlib.Path(__file__).resolve().parent.parent / '.env')

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Test database connection by executing a simple query
def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return "Database connected successfully"
    except Exception as e:
        return f"Database connection failed: {str(e)}"
