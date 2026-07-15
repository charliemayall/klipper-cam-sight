from ..common import RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from ..server import Server as Server
from .database import MoonrakerDatabase as MoonrakerDatabase
from .http_client import HttpClient as HttpClient
from .machine import Machine as Machine
from .shell_command import ShellCommandFactory as ShellCommandFactory
from _typeshed import Incomplete
from typing import Any

CAM_FIELDS: Incomplete

class WebcamManager:
    server: Incomplete
    webcams: dict[str, WebCam]
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def get_webcams(self) -> dict[str, WebCam]: ...
    def get_cam_by_uid(self, uid: str) -> WebCam: ...

class WebCam:
    name: str
    enabled: bool
    icon: str
    aspect_ratio: str
    target_fps: int
    target_fps_idle: int
    location: str
    service: str
    stream_url: str
    snapshot_url: str
    flip_horizontal: bool
    flip_vertical: bool
    rotation: int
    source: str
    extra_data: dict[str, Any]
    uid: str
    def __init__(self, server: Server, **kwargs) -> None: ...
    def as_dict(self): ...
    async def get_stream_url(self, convert_local: bool = False) -> str: ...
    async def get_snapshot_url(self, convert_local: bool = False) -> str: ...
    async def convert_local(self, url: str) -> str: ...
    def update(self, web_request: WebRequest) -> None: ...
    @staticmethod
    def set_default_host(host: str) -> None: ...
    @classmethod
    def from_config(cls, config: ConfigHelper) -> WebCam: ...
    @classmethod
    def from_web_request(cls, server: Server, web_request: WebRequest, uid: str) -> WebCam: ...
    @classmethod
    def from_database(cls, server: Server, cam_data: dict[str, Any]) -> WebCam: ...

def load_component(config: ConfigHelper) -> WebcamManager: ...
