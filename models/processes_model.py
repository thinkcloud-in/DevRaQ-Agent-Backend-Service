from pydantic import BaseModel
from typing import Optional


class KillRequest(BaseModel):
    host: str
    IP: Optional[str] = None  # Add IP field as optional
    pids: list[int]