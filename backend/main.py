from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.database_test import test_db_connection  # import the DB test function
from app.controllers.chore_controller import router as chore_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.user_controller import router as user_router
from app.controllers.household_controller import router as household_router
from app.controllers.notification_controller import router as notification_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # limit to frontend URL in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chore_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(household_router)
app.include_router(notification_router)


@app.get("/")
def root():
    return {"message": "Backend running"}

# Test Database Connection
# @app.get("/test-db")
# def test_database():
#     return {"message": test_db_connection()