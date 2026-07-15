import asyncio
from ..confighelper import ConfigHelper as ConfigHelper
from ..server import Server as Server
from _typeshed import Incomplete
from serial import Serial, SerialException
from typing import Awaitable, Callable

READER_LIMIT: Incomplete

class AsyncSerialConnection:
    error = SerialException
    name: Incomplete
    eventloop: Incomplete
    port: Incomplete
    baud: Incomplete
    ser: Serial | None
    send_task: asyncio.Task | None
    send_buffer: list[tuple[asyncio.Future, bytes]]
    def __init__(self, server: Server, name: str, port: str, baud: int) -> None: ...
    @property
    def connected(self) -> bool: ...
    @property
    def reader(self) -> asyncio.StreamReader: ...
    @property
    def reader_active(self) -> bool: ...
    @staticmethod
    def from_config(config: ConfigHelper, default_baud: int = 57600) -> AsyncSerialConnection: ...
    def set_read_callback(self, callback: Callable[[bytes], None] | None, force: bool = False) -> None: ...
    def close(self) -> Awaitable: ...
    def open(self, exclusive: bool = True) -> None: ...
    def send(self, data: bytes) -> asyncio.Future: ...
