import uuid
import contextvars
from fastapi import Request, Response

# Context variable to store request ID per request
request_id_var = contextvars.ContextVar("request_id", default="-")

def add_request_id(request: Request, call_next):
    """FastAPI middleware that ensures each request has a unique ID.
    If the client supplies an `X-Request-ID` header, that value is used;
    otherwise a new UUID4 is generated.
    The ID is stored in a context variable so the logging filter can
    include it in every log record. The response also carries the header
    for client visibility.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(request_id)
    response: Response = call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
