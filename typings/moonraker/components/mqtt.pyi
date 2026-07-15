import asyncio
import paho.mqtt.client as paho_mqtt
import socket
from ..common import APIDefinition as APIDefinition, APITransport as APITransport, JsonRPC as JsonRPC, KlippyState as KlippyState, RequestType as RequestType, TransportType as TransportType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from ..eventloop import FlexTimer as FlexTimer
from .klippy_apis import KlippyAPI as KlippyAPI
from _typeshed import Incomplete
from paho.mqtt.properties import Properties as Properties
from typing import Any, Awaitable, Callable, Coroutine, Deque

FlexCallback = Callable[[bytes], Coroutine | None]
RPCCallback = Callable[..., Coroutine]
PAHO_MQTT_VERSION: Incomplete
DUP_API_REQ_CODE: int
MQTT_PROTOCOLS: Incomplete

class ExtPahoClient(paho_mqtt.Client):
    def reconnect(self, sock: socket.socket | None = None): ...

class SubscriptionHandle:
    callback: Incomplete
    topic: Incomplete
    def __init__(self, topic: str, callback: FlexCallback) -> None: ...

class BrokerAckLogger:
    topics: Incomplete
    action: Incomplete
    def __init__(self, topics: list[str], action: str) -> None: ...
    def __call__(self, fut: asyncio.Future) -> None: ...
SubscribedDict = dict[str, tuple[int, list[SubscriptionHandle]]]

class AIOHelper:
    loop: Incomplete
    client: Incomplete
    misc_task: asyncio.Task | None
    def __init__(self, client: paho_mqtt.Client) -> None: ...
    async def misc_loop(self) -> None: ...

class MQTTClient(APITransport):
    server: Incomplete
    eventloop: Incomplete
    address: str
    port: int
    tls_enabled: bool
    user_name: str | None
    password: str | None
    protocol: Incomplete
    instance_name: Incomplete
    qos: Incomplete
    publish_split_status: Incomplete
    client: Incomplete
    connect_evt: asyncio.Event
    disconnect_evt: asyncio.Event | None
    connect_task: asyncio.Task | None
    subscribed_topics: SubscribedDict
    pending_responses: list[asyncio.Future]
    pending_acks: dict[int, asyncio.Future]
    api_request_topic: Incomplete
    api_resp_topic: Incomplete
    klipper_status_topic: Incomplete
    klipper_state_prefix: Incomplete
    moonraker_status_topic: Incomplete
    status_interval: Incomplete
    status_cache: dict[str, dict[str, Any]]
    status_update_timer: FlexTimer | None
    last_status_time: float
    status_objs: dict[str, list[str] | None]
    timestamp_deque: Deque
    api_qos: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    helper: Incomplete
    async def component_init(self) -> None: ...
    async def wait_connection(self, timeout: float | None = None) -> bool: ...
    def is_connected(self) -> bool: ...
    def subscribe_topic(self, topic: str, callback: FlexCallback, qos: int | None = None) -> SubscriptionHandle: ...
    def unsubscribe(self, hdl: SubscriptionHandle) -> None: ...
    def publish_topic(self, topic: str, payload: Any = None, qos: int | None = None, retain: bool = False) -> Awaitable[None]: ...
    async def publish_topic_with_response(self, topic: str, response_topic: str, payload: Any = None, qos: int | None = None, retain: bool = False, timeout: float | None = None) -> bytes: ...
    @property
    def transport_type(self) -> TransportType: ...
    def screen_rpc_request(self, api_def: APIDefinition, req_type: RequestType, args: dict[str, Any]) -> None: ...
    def send_status(self, status: dict[str, Any], eventtime: float) -> None: ...
    def get_instance_name(self) -> str: ...
    async def close(self) -> None: ...

def load_component(config: ConfigHelper) -> MQTTClient: ...
