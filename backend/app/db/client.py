"""
Module for creating and returning the Supabase client.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

from supabase import Client, create_client
from app.utils import load_env_variables

client = None


def get_client() -> Client:
    """
    Create and cache a client to connect with the Supabase database.

    Output:
        A Supabase Client object that can be used to interact with the database.

    Raises:
        ValueError: if required environment variables are missing.
    """
    global client

    if client is not None:
        return client

    env = load_env_variables()
    supabase_url = env["SUPABASE_URL"]
    service_key = env["SERVICE_KEY"]

    if supabase_url is None:
        raise ValueError("SUPABASE_URL not found in .env")

    if service_key is None:
        raise ValueError("SERVICE_KEY not found in .env")

    client = create_client(supabase_url, service_key)
    return client