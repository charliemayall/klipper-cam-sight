import asyncio
from ..common import KlippyState as KlippyState, RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .http_client import HttpClient as HttpClient
from .klippy_connection import KlippyConnection as KlippyConnection
from .machine import Machine as Machine
from .mqtt import MQTTClient as MQTTClient
from .shell_command import ShellCommandFactory as ShellCommand
from _typeshed import Incomplete
from typing import Any, Coroutine

class PrinterPower:
    server: Incomplete
    devices: dict[str, PowerDevice]
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def set_device_power(self, device: str, state: bool | str, force: bool = False) -> None: ...
    async def add_device(self, name: str, device: PowerDevice) -> None: ...
    async def close(self) -> None: ...

class PowerDevice:
    server: Incomplete
    name: Incomplete
    type: str
    state: str
    request_lock: Incomplete
    init_task: asyncio.Task | None
    locked_while_printing: Incomplete
    off_when_shutdown: Incomplete
    off_when_shutdown_delay: float
    shutdown_timer_handle: asyncio.TimerHandle | None
    restart_delay: float
    klipper_restart: Incomplete
    bound_services: list[str]
    need_scheduled_restart: bool
    on_when_queued: Incomplete
    initial_state: bool | None
    restrict_actions: Incomplete
    def __init__(self, config: ConfigHelper, can_poll: bool = True) -> None: ...
    def get_name(self) -> str: ...
    def get_device_info(self) -> dict[str, Any]: ...
    def notify_power_changed(self) -> None: ...
    async def process_power_changed(self) -> None: ...
    async def process_bound_services(self) -> None: ...
    def process_klippy_shutdown(self) -> None: ...
    def should_turn_on_when_queued(self) -> bool: ...
    def init_state(self) -> Coroutine | None: ...
    def initialize(self) -> bool: ...
    async def process_request(self, req: str, force: bool = False) -> str: ...
    def refresh_status(self) -> Coroutine | None: ...
    def set_power(self, state: str) -> Coroutine | None: ...
    def start_polling(self) -> bool: ...
    def stop_polling(self) -> Coroutine | None: ...
    def close(self) -> Coroutine | None: ...

class HTTPDevice(PowerDevice):
    client: HttpClient
    user: Incomplete
    password: Incomplete
    has_basic_auth: bool
    addr: str
    port: Incomplete
    protocol: Incomplete
    def __init__(self, config: ConfigHelper, default_port: int = -1, default_user: str = '', default_password: str = '', default_protocol: str = 'http', is_generic: bool = False) -> None: ...
    def enable_basic_authentication(self) -> None: ...
    init_task: Incomplete
    state: Incomplete
    async def init_state(self) -> None: ...
    async def refresh_status(self) -> None: ...
    async def set_power(self, state) -> None: ...

class GpioDevice(PowerDevice):
    timer: float | None
    timer_handle: asyncio.TimerHandle | None
    gpio_out: Incomplete
    def __init__(self, config: ConfigHelper, initial_val: int | None = None) -> None: ...
    async def init_state(self) -> None: ...
    def refresh_status(self) -> None: ...
    state: str
    def set_power(self, state) -> None: ...
    def close(self) -> None: ...

class KlipperDevice(PowerDevice):
    is_shutdown: bool
    update_fut: asyncio.Future | None
    timer: float | None
    timer_handle: asyncio.TimerHandle | None
    object_name: Incomplete
    gc_cmd: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    def get_device_info(self) -> dict[str, Any]: ...
    def process_klippy_shutdown(self) -> None: ...
    state: str
    async def refresh_status(self) -> None: ...
    async def set_power(self, state: str) -> None: ...
    def close(self) -> None: ...

class RFDevice(GpioDevice):
    ZERO_BIT: Incomplete
    ONE_BIT: Incomplete
    SYNC_BIT: Incomplete
    PULSE_LEN: float
    RETRIES: int
    on: Incomplete
    off: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    state: str
    def set_power(self, state) -> None: ...

class TPLinkSmartPlug(PowerDevice):
    START_KEY: int
    timer: Incomplete
    addr: Incomplete
    output_id: int | None
    port: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    init_task: Incomplete
    state: Incomplete
    async def init_state(self) -> None: ...
    async def refresh_status(self) -> None: ...
    async def set_power(self, state) -> None: ...

class Tasmota(HTTPDevice):
    output_id: Incomplete
    timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...

class Shelly(HTTPDevice):
    output_id: Incomplete
    timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...

class SmartThings(HTTPDevice):
    device: str
    token: str
    def __init__(self, config: ConfigHelper) -> None: ...

class HomeSeer(HTTPDevice):
    device: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...

class HomeAssistant(HTTPDevice):
    device: str
    token: str
    domain: str
    status_delay: float
    def __init__(self, config: ConfigHelper) -> None: ...

class Loxonev1(HTTPDevice):
    output_id: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...

class MQTTDevice(PowerDevice):
    mqtt: MQTTClient
    eventloop: Incomplete
    cmd_topic: str
    cmd_payload: Incomplete
    retain_cmd_state: Incomplete
    query_topic: str | None
    query_payload: Incomplete
    must_query: Incomplete
    last_request: str
    response_count: int
    state_topic: str
    state_timeout: Incomplete
    state_response: Incomplete
    qos: int | None
    query_response: asyncio.Future | None
    def __init__(self, config: ConfigHelper) -> None: ...
    state: str
    async def refresh_status(self) -> None: ...
    async def set_power(self, state: str) -> None: ...

class HueDevice(HTTPDevice):
    device_id: Incomplete
    device_type: Incomplete
    state_key: str
    on_state: str
    def __init__(self, config: ConfigHelper) -> None: ...

class GenericHTTP(HTTPDevice):
    urls: dict[str, str]
    request_template: Incomplete
    response_template: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...

HUB_STATE_PATTERN: str

class UHubCtl(PowerDevice):
    scmd: ShellCommand
    location: Incomplete
    port: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def init_state(self) -> None: ...
    state: str
    async def refresh_status(self, is_init: bool = False) -> None: ...
    async def set_power(self, state: str) -> None: ...

def load_component(config: ConfigHelper) -> PrinterPower: ...
