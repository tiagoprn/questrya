from pydantic import BaseModel


class GenericClientResponseError(BaseModel):
    """
    Use this when the error was caused by the client.
    (status_code: 4xx)

    E.g. invalid request parameters, etc...
    """

    error: str


class GenericServerResponseError(BaseModel):
    """
    Use this when the error was caused by the server.
    (status_code: 5xx)

    E.g. infinite loop, connection to external server timed out, etc..
    """

    error: str
