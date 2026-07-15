from _typeshed import Incomplete
from typing import Any

class ServerError(Exception):
    status_code: Incomplete
    def __init__(self, message: str, status_code: int = 400) -> None: ...

class AgentError(ServerError):
    error_data: Incomplete
    def __init__(self, message: str, error_data: Any) -> None: ...
