from fastapi import APIRouter, HTTPException, status, FastAPI
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import chore, database

app = FastAPI()

@app.get("/chores/{householdid}")
def get_user(householdid: int):
    chores = database.get_chores(householdid)

    chore_responses = []
    for c in chores:
        response = {"name" : c.name, 
                    "description" : c.description, 
                    "request_date" : c.request_date.strftime("%s") ,
                    "due_date" : c.due_date.strftime("%s"),
                    "assignee": c.assignee.fname + " " + c.assignee.lname,
                    "status": c.status.name
                    }
        chore_responses.append(response)

    return chore_responses