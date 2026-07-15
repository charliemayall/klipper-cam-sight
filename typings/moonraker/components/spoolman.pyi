import asyncio
from ..common import HistoryFieldData as HistoryFieldData, RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .announcements import Announcements as Announcements
from .database import MoonrakerDatabase as MoonrakerDatabase
from .history import History as History
from .http_client import HttpClient as HttpClient, HttpResponse as HttpResponse
from .klippy_apis import KlippyAPI as APIComp
from _typeshed import Incomplete
from tornado.websocket import WebSocketClientConnection as WebSocketClientConnection

DB_NAMESPACE: str
ACTIVE_SPOOL_KEY: str

class SpoolManager:
    server: Incomplete
    eventloop: Incomplete
    sync_rate_seconds: Incomplete
    report_timer: Incomplete
    pending_reports: dict[int, float]
    spoolman_ws: WebSocketClientConnection | None
    connection_task: asyncio.Task | None
    spool_check_task: asyncio.Task | None
    ws_connected: bool
    reconnect_delay: float
    is_closing: bool
    spool_id: int | None
    spool_history: Incomplete
    klippy_apis: APIComp
    http_client: HttpClient
    database: MoonrakerDatabase
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def connected(self) -> bool: ...
    def set_active_spool(self, spool_id: int | None) -> None: ...
    async def report_extrusion(self, eventtime: float) -> float: ...
    async def close(self) -> None: ...

def load_component(config: ConfigHelper) -> SpoolManager: ...
