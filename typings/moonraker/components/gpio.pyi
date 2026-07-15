import asyncio
import periphery
from ..confighelper import ConfigHelper as ConfigHelper
from ..eventloop import EventLoop as EventLoop
from ..utils import KERNEL_VERSION as KERNEL_VERSION
from _typeshed import Incomplete
from typing import Any, Awaitable, Callable

GpioEventCallback = Callable[[float, float, int], Awaitable[None] | None]
GPIO_PATTERN: str
BIAS_FLAG_TO_DESC: dict[str, str]

class GpioFactory:
    server: Incomplete
    reserved_gpios: dict[str, GpioBase]
    def __init__(self, config: ConfigHelper) -> None: ...
    def setup_gpio_out(self, pin_name: str, initial_value: int = 0) -> GpioOutputPin: ...
    def register_gpio_event(self, pin_name: str, callback: GpioEventCallback) -> GpioEvent: ...
    def close(self) -> None: ...

class GpioBase:
    orig: str
    name: str
    inverted: bool
    gpio: Incomplete
    value: int
    def __init__(self, gpio: periphery.GPIO, pin_params: dict[str, Any]) -> None: ...
    def close(self) -> None: ...
    def is_inverted(self) -> bool: ...
    def get_value(self) -> int: ...
    def get_name(self) -> str: ...

class GpioOutputPin(GpioBase):
    value: Incomplete
    def write(self, value: int) -> None: ...

MAX_ERRORS: int
ERROR_RESET_TIME: float

class GpioEvent(GpioBase):
    event_loop: Incomplete
    callback: Incomplete
    on_error: Callable[[str], None] | None
    debounce_period: float
    last_event_time: float
    error_count: int
    last_error_reset: float
    started: bool
    debounce_task: asyncio.Task | None
    def __init__(self, event_loop: EventLoop, gpio: periphery.GPIO, pin_params: dict[str, Any], callback: GpioEventCallback) -> None: ...
    def fileno(self) -> int: ...
    def setup_debounce(self, debounce_period: float, err_callback: Callable[[str], None] | None) -> None: ...
    value: Incomplete
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...

def load_component(config: ConfigHelper) -> GpioFactory: ...
