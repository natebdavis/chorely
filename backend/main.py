"""
Main entry point for the Chorely backend application.

Contributers: Gilligan Berlinski, Edmund Krajewski
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth_controller import router as auth_router
from app.controllers.chore_controller import router as chore_router
from app.controllers.household_controller import router as household_router
from app.controllers.invite_controller import router as invite_router
from app.controllers.notification_controller import router as notification_router
from app.controllers.user_controller import router as user_router
from app.controllers.request_controller import router as request_router
from app.controllers.chore_template_controller import router as chore_template_router
from app.controllers.leaderboard_controller import router as leaderboard_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chore_router)
app.include_router(household_router)
app.include_router(invite_router)
app.include_router(notification_router)
app.include_router(user_router)
app.include_router(request_router)
app.include_router(chore_template_router)
app.include_router(leaderboard_router)

@app.get("/")
def root():
    """Root endpoint to verify that the backend is running."""
    return {"message": "Backend is running"}