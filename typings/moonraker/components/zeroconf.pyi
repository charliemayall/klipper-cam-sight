import asyncio
from ..common import RequestType as RequestType, TransportType as TransportType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .application import MoonrakerApp as MoonrakerApp
from .machine import Machine as Machine
from _typeshed import Incomplete
from typing import Any
from zeroconf import IPVersion
from zeroconf.asyncio import AsyncServiceInfo, AsyncZeroconf

ZC_SERVICE_TYPE: str

class AsyncRunner:
    ip_version: Incomplete
    aiozc: AsyncZeroconf | None
    def __init__(self, ip_version: IPVersion) -> None: ...
    async def register_services(self, infos: list[AsyncServiceInfo]) -> None: ...
    async def unregister_services(self, infos: list[AsyncServiceInfo]) -> None: ...
    async def update_services(self, infos: list[AsyncServiceInfo]) -> None: ...

class ZeroconfRegistrar:
    server: Incomplete
    mdns_name: Incomplete
    ip_version: Incomplete
    runner: Incomplete
    cfg_addr: Incomplete
    bound_all: Incomplete
    ssdp_server: SSDPServer | None
    def __init__(self, config: ConfigHelper) -> None: ...
    service_info: Incomplete
    async def component_init(self) -> None: ...
    async def close(self) -> None: ...

SSDP_ADDR: Incomplete
SSDP_SERVER_ID: str
SSDP_MAX_AGE: int
SSDP_DEVICE_TYPE: str
SSDP_DEVICE_XML: Incomplete

class SSDPServer(asyncio.protocols.DatagramProtocol):
    server: Incomplete
    unique_id: Incomplete
    name: str
    base_url: str
    response_headers: list[str]
    registered: bool
    running: bool
    close_fut: asyncio.Future | None
    response_handle: asyncio.TimerHandle | None
    boot_id: Incomplete
    config_id: int
    ad_timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    advertisements: Incomplete
    def register_service(self, name: str, host_name_or_ip: str, port: int) -> None: ...
    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None: ...
    def connection_lost(self, exc: Exception | None) -> None: ...
    def pause_writing(self) -> None: ...
    def resume_writing(self) -> None: ...
    def datagram_received(self, data: bytes, addr: tuple[str | Any, int]) -> None: ...
    def error_received(self, exc: Exception) -> None: ...

def load_component(config: ConfigHelper) -> ZeroconfRegistrar: ...
