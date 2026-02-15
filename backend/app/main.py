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

# ------------------------
# New route to test DB
# ------------------------
@app.get("/test-db")
def test_database():
    return {"message": test_db_connection()}