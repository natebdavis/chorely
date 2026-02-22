from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_db_connection  # import the DB test function

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # limit to frontend URL in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend running"}

# Test Database Connection
@app.get("/test-db")
def test_database():
    return {"message": test_db_connection()}

# Tests if backend is running and can connect to the database.
def test_backend():
    message = root()["message"]
    print(message)  # Print backend test message on startup
    message = test_database()["message"]
    print(message)  # Print DB connection result on startup