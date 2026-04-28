"""
Module for chore request related database operations.

Contributors: Gilligan Berlinski
"""
from supabase import Client
from typing import Union, Iterable

from app.db.client import get_client
from app.db.user_repo import get_requester, get_user
from app.request import RequestStatus, create_RequestResponse, RequestResponse, RequestCreateRequest, RequestUpdateRequest, Request_Col_Name, Request_View_Col_Name, REQUEST_TABLE_NAME, REQUEST_VIEW


first = 0

def create_request(request: RequestCreateRequest, 
                client: Union[Client, None] = None)-> Union[RequestResponse, None]:

    """
    Create a request in the database.

    Output:
        Created request data returned as RequestResponse, or None if creation failed.

    Raises:
        Value Error if chore id does not correspond to an existing chore in the database.
        Value Error if requested assignee user id does not correspond to an existing user in the database.
    """
    
    if client is None:
        client = get_client()

    requester = get_requester(request.requested_choreid, client=client)

    if requester is None:
        raise ValueError(f"Chore id: {request.requested_choreid} does not exist.")
    
    requested_assignee = get_user(userid=request.requested_assignee_userid, client=client)

    if requested_assignee is None:
        raise ValueError(f"Requested assignee user id: {request.requested_assignee_userid} does not exist.")

    data = {
        Request_Col_Name.chorerequestid.value: request.requested_choreid,
        Request_Col_Name.requestedassigneeid.value: request.requested_assignee_userid,
        Request_Col_Name.chorerequestid.value: request.requested_choreid
    }

    response = client.table(REQUEST_TABLE_NAME).insert(data).execute()
    request_rows = response.data

    if not request_rows:
        return None
    
    response = (
        client
        .table(REQUEST_VIEW)
        .select("*")
        .eq(Request_Col_Name.requestid.value, request_rows[first][Request_Col_Name.requestid.value])
        .execute()
    )
    
    return create_RequestResponse(data=response.data[first])

def get_request(request_id: int, client: Union[Client, None] = None) -> Union[RequestResponse, None]:
    """
    Get a request by its request id.

    Output:
        A RequestResponse object for the request, or None if the request does not exist.
    """

    if client is None:
        client = get_client()

    response = (
        client
        .table(REQUEST_VIEW)
        .select("*")
        .eq(Request_Col_Name.requestid.value, request_id)
        .execute()
    )

    data = response.data
    if not data:
        return None
    
    return create_RequestResponse(data=data[first])

def update_request(requestid: int, request: RequestUpdateRequest, 
                   client: Union[Client, None] = None) -> Union[RequestResponse, None]:
    """
    Update a request's status in the database.

    Output:
        Updated request data returned as RequestResponse, or None if update failed.
    """
    
    if client is None:
        client = get_client()

    data = {
        Request_Col_Name.requeststatus.value: request.updated_status.value,
        Request_Col_Name.respondedat.value: request.responded_at
    }

    response = (
        client
        .table(REQUEST_TABLE_NAME)
        .update(data)
        .eq(Request_Col_Name.requestid.value, requestid).execute()
    )

    rows = response.data
    if not rows:
        raise ValueError(f"Request with id: {requestid} does not exist.")
    
    response = (
        client
        .table(REQUEST_VIEW)
        .select("*")
        .eq(Request_Col_Name.requestid.value, requestid)
        .execute()
    )

    data = response.data
    if not data:
        return None
    
    return create_RequestResponse(data=data[first])

def get_outgoing_pending_requests(requester_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    
    """
     Get all outgoing pending requests for a requester. 
    
    Output:
        An iterable of RequestResponse objects for the requester's outgoing pending requests, or None if there are no outgoing pending requests.
    """
    
    if client is None:
        client = get_client()

    response = (
    client
    .table(REQUEST_VIEW)
    .select("*")
    .eq(Request_View_Col_Name.requesterid.value, requester_id)
    .eq(Request_Col_Name.requeststatus.value, RequestStatus.PENDING.value)
    .execute()
)

    data = response.data
    if not data:
        return None

    return [create_RequestResponse(data=row) for row in data]


def get_user_requests(requestee_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    """
    Get all requests for a user, including both pending and responded requests.
    
    Output:
        An iterable of RequestResponse objects for the user's requests, or None if there are no requests
    """
    if client is None:
        client = get_client()

    response = (
    client
    .table(REQUEST_VIEW)
    .select("*")
    .eq(Request_Col_Name.requestedassigneeid.value, requestee_id)
    .eq(Request_Col_Name.requeststatus.value, RequestStatus.PENDING.value)
    .execute()
)

    if not response.data:
        return None

    return [create_RequestResponse(data=row) for row in response.data]

    

    