from typing import Iterable

from fastapi import APIRouter, HTTPException, Depends, status
from app.user import UserResponse
from app.database import get_current_user
from app.request import RequestResponse



router = APIRouter(prefix="/requests", tags=["requests"])

@router.get("", response_model=Iterable[RequestResponse])
def get_my_pending_requests(
    current_user: UserResponse = Depends(get_current_user),
):
    pass


@router.get("/outgoing", response_model=Iterable[RequestResponse])
def get_my_outgoing_pending_requests(
    current_user: UserResponse = Depends(get_current_user),
):
    pass


@router.post("/{requestid}/accept")
def accept_request(
    requestid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    pass


@router.post("/{requestid}/decline")
def reject_request(
    requestid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    pass