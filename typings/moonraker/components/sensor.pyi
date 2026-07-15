from ..common import HistoryFieldData as HistoryFieldData, RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .history import History as History
from .mqtt import MQTTClient as MQTTClient
from _typeshed import Incomplete
from typing import Any, DefaultDict, Deque

SENSOR_UPDATE_TIME: float
SENSOR_EVENT_NAME: str

class BaseSensor:
    server: Incomplete
    error_state: str | None
    id: Incomplete
    type: Incomplete
    name: Incomplete
    last_measurements: dict[str, int | float]
    last_value: dict[str, int | float]
    values: DefaultDict[str, Deque[int | float]]
    param_info: list[dict[str, str]]
    field_info: dict[str, list[HistoryFieldData]]
    def __init__(self, config: ConfigHelper) -> None: ...
    async def initialize(self) -> bool: ...
    def get_sensor_info(self, extended: bool = False) -> dict[str, Any]: ...
    def get_sensor_measurements(self) -> dict[str, list[int | float]]: ...
    def get_name(self) -> str: ...
    def close(self) -> None: ...

class MQTTSensor(BaseSensor):
    mqtt: MQTTClient
    state_topic: str
    state_response: Incomplete
    qos: int | None
    def __init__(self, config: ConfigHelper) -> None: ...
    error_state: Incomplete
    async def initialize(self) -> bool: ...

class Sensors:
    server: Incomplete
    sensors: dict[str, BaseSensor]
    sensors_update_timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def close(self) -> None: ...

def load_component(config: ConfigHelper) -> Sensors: ...
