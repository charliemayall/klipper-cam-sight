import pathlib
from ..common import RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .application import MoonrakerApp as MoonrakerApp
from .authorization import Authorization as Authorization
from .file_manager.file_manager import FileManager as FileManager
from .http_client import HttpClient as HttpClient
from .klippy_connection import KlippyConnection as KlippyConnection
from .machine import Machine as Machine
from .shell_command import ShellCommandFactory as ShellCommandFactory
from .update_manager.update_manager import UpdateManager as UpdateManager
from _typeshed import Incomplete
from typing import Any

StrOrPath = str | pathlib.Path
ESTIMATOR_URL: str
UPDATE_CONFIG: Incomplete
RELEASE_INFO: Incomplete
IDENT_REGEX: str

class GcodeAnalysis:
    server: Incomplete
    cmd_lock: Incomplete
    file_manger: FileManager
    estimator_timeout: Incomplete
    auto_analyze: Incomplete
    auto_dump_defcfg: Incomplete
    default_config: Incomplete
    estimator_config: Incomplete
    estimator_path: pathlib.Path | None
    estimator_ready: bool
    estimator_version: str
    updater_registered: bool
    proc_config: dict[str, Any]
    def __init__(self, config: ConfigHelper) -> None: ...
    @property
    def estimator_version_tuple(self) -> tuple[int, ...]: ...
    async def component_init(self) -> None: ...
    async def estimate_file(self, gc_path: pathlib.Path, est_config: pathlib.Path | None = None) -> dict[str, Any]: ...
    async def post_process_file(self, gc_path: pathlib.Path, est_config: pathlib.Path | None = None, force: bool = False) -> dict[str, Any]: ...

def load_component(config: ConfigHelper) -> GcodeAnalysis: ...
