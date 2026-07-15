import json
from _typeshed import Incomplete
from typing import Any

def dumps(obj: Any) -> bytes: ...
def loads(data: str | bytes | bytearray) -> Any: ...

MSGSPEC_ENABLED: bool
encoder: Incomplete
decoder: Incomplete
dumps: Incomplete
loads: Incomplete
loads = json.loads
