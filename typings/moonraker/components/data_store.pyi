from ..common import RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .klippy_connection import KlippyConnection as KlippyConnection
from _typeshed import Incomplete
from typing import Any, Deque

GCQueue = Deque[dict[str, Any]]
TempStore = dict[str, dict[str, Deque[float | None]]]
TEMP_UPDATE_TIME: float

class DataStore:
    server: Incomplete
    temp_store_size: Incomplete
    gcode_store_size: Incomplete
    subscription_cache: Incomplete
    gcode_queue: GCQueue
    temperature_store: TempStore
    temp_monitors: list[str]
    temp_update_timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def close(self) -> None: ...

def load_component(config: ConfigHelper) -> DataStore: ...
