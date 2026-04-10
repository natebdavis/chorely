from supabase import Client
from typing import Union, Iterable

from app.db.client import get_client
from app.db.chore_repo import get_requesterid
from app.request import create_RequestResponse, RequestResponse, RequestCreateRequest, RequestUpdateRequest, Request_Col_Name, REQUEST_TABLE_NAME

first = 0

"""
Module for chore request related database operations.

Contributors: Gilligan Berlinski
"""

def add_request(request: RequestCreateRequest, 
                client: Union[Client, None] = None)-> Union[RequestResponse, None]:

    """
    Add a request to the database.

    Output:
        Inserted request data returned as RequestResponse, or None if insert failed.

    Raises:
        Value Error if chore id does not correspond to an existing chore in the database.
    """
    
    if client is None:
        client = get_client()

    requester_id = get_requesterid(request.requested_choreid)

    if requester_id is None:
        raise ValueError(f"Chore id: {request.requested_choreid} does not exist.")

    data = {
        Request_Col_Name.chorerequestid: request.requested_choreid,
        Request_Col_Name.requestedassigneeid: request.requested_assignee_userid,
        Request_Col_Name.chorerequestid: request.requested_choreid
    }

    response = client.table(REQUEST_TABLE_NAME).insert(data).execute()
    request_rows = response.data

    if not request_rows:
        return None
    
    return create_RequestResponse(data=request_rows[first], requesterid=requester_id)

def get_request(request_id: int, client: Union[Client, None] = None) -> Union[RequestResponse, None]:
    pass

def update_request(request: RequestUpdateRequest, 
                   client: Union[Client, None] = None) -> Union[RequestResponse, None]:
    pass

def get_outgoing_pending_requests(requester_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    pass

def get_user_requests(requestee_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    pass


    

    