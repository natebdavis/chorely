from supabase import Client
from typing import Union, Iterable

from app.db.client import get_client
from app.db.chore_repo import get_all_requested_chores
from app.db.user_repo import get_requester, get_user
from app.request import RequestStatus, create_RequestResponse, RequestResponse, RequestCreateRequest, RequestUpdateRequest, Request_Col_Name, REQUEST_TABLE_NAME
from app.user import User_Col_Name, USER_TABLE_NAME
from app.chore import Chore_Col_Name, CHORE_TABLE_NAME

first = 0

"""
Module for chore request related database operations.

Contributors: Gilligan Berlinski
"""

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
    
    return create_RequestResponse(data=request_rows[first], requesterid=requester.userid, requester_name=requester.username, requested_assignee_name=requested_assignee.username)

def get_request(request_id: int, client: Union[Client, None] = None) -> Union[RequestResponse, None]:

    if client is None:
        client = get_client()

    response = (
        client
        .table(REQUEST_TABLE_NAME)
        .select("*")
        .eq(Request_Col_Name.requestid.value, request_id)
        .execute()
    )

    data = response.data
    if not data:
        return None
    

    requester = get_requester(data[first][Request_Col_Name.chorerequestid.value], client=client)
    requested_assignee = get_user(userid=data[first][Request_Col_Name.requestedassigneeid.value], client=client)

    return create_RequestResponse(data=data[first], requesterid=requester.userid, requester_name=requester.username, requested_assignee_name=requested_assignee.username)

def update_request(requestid: int, request: RequestUpdateRequest, 
                   client: Union[Client, None] = None) -> Union[RequestResponse, None]:
    
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
    
    return create_RequestResponse(data=rows[first], requesterid=rows[first][Request_Col_Name.chorerequestid.value], requester_name=get_requester(rows[first][Request_Col_Name.chorerequestid.value], client=client).username, 
                                  requested_assignee_name=get_user(userid=rows[first][Request_Col_Name.requestedassigneeid.value], client=client).username)

def get_outgoing_pending_requests(requester_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    
    if client is None:
        client = get_client()

    chores = get_all_requested_chores(userid=requester_id, client=client)

    if not chores:
        return None

    chore_ids = [chore.choreid for chore in chores]

    response = (
    client
    .table(REQUEST_TABLE_NAME)
    .select(f"""
        *,
        {Request_Col_Name.requestedassigneeid.value},
         {USER_TABLE_NAME} (
            {User_Col_Name.userid.value},
            {User_Col_Name.username.value}
        )
    """)
    .in_(Request_Col_Name.chorerequestid.value, chore_ids)
    .eq(Request_Col_Name.requeststatus.value, RequestStatus.PENDING.value)
    .execute()
)

    if not response.data:
        return None

    requester = get_user(userid=requester_id, client=client)


    return [create_RequestResponse(data=row, requesterid=requester_id, requester_name=requester.username, 
                                   requested_assignee_name=row.get(Request_Col_Name.requestedassigneeid.value).get(User_Col_Name.username.value)) for row in response.data]


def get_user_requests(requestee_id: int, 
                      client: Union[Client, None] = None) -> Union[Iterable[RequestResponse], None]:
    if client is None:
        client = get_client()

    response = (
    client
    .table(REQUEST_TABLE_NAME)
    .select(f"""
        {Request_Col_Name.requestid.value},
        {Request_Col_Name.chorerequestid.value},
        {Request_Col_Name.requeststatus.value},

        {CHORE_TABLE_NAME} (
            {Chore_Col_Name.choreid.value},
            {Chore_Col_Name.requester.value},
            {USER_TABLE_NAME} (
                {User_Col_Name.userid.value},
                {User_Col_Name.username.value}
            )
        )
    """)
    .eq(Request_Col_Name.requestedassigneeid.value, requestee_id)
    .eq(Request_Col_Name.requeststatus.value, RequestStatus.PENDING.value)
    .execute()
    )

    if not response.data:
        return None

    requestee = get_user(userid=requestee_id, client=client)

    return [create_RequestResponse(data=row, requesterid=row[CHORE_TABLE_NAME][Chore_Col_Name.requester.value], 
                                   requester_name=row[CHORE_TABLE_NAME][USER_TABLE_NAME][User_Col_Name.username.value], 
                                   requested_assignee_name=requestee.username) for row in response.data]

    

    