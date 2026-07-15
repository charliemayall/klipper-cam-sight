import pathlib
from ...confighelper import ConfigHelper as ConfigHelper
from ...utils import pip_utils as pip_utils
from ...utils.sysdeps_parser import SysDepsParser as SysDepsParser
from ..file_manager.file_manager import FileManager as FileManager
from ..machine import Machine as Machine
from .base_deploy import BaseDeploy as BaseDeploy
from .common import AppType as AppType, Channel as Channel
from _typeshed import Incomplete
from datetime import datetime
from typing import Any

PIPVER_CHECK_DAYS: int

class AppDeploy(BaseDeploy):
    config: Incomplete
    type: Incomplete
    channel: Incomplete
    channel_invalid: bool
    report_anomalies: Incomplete
    virtualenv: pathlib.Path | None
    py_exec: pathlib.Path | None
    pip_cmd: str | None
    pip_version_info: pip_utils.PipVersionInfo | None
    pip_ver_date: datetime
    venv_args: str | None
    npm_pkg_json: pathlib.Path | None
    python_reqs: pathlib.Path | None
    install_script: pathlib.Path | None
    system_deps_json: pathlib.Path | None
    info_tags: list[str]
    managed_services: list[str]
    def __init__(self, config: ConfigHelper, prefix: str) -> None: ...
    async def initialize(self) -> dict[str, Any]: ...
    def get_configured_type(self) -> AppType: ...
    def check_same_paths(self, app_path: str | pathlib.Path, executable: str | pathlib.Path) -> bool: ...
    async def recover(self, hard: bool = False, force_dep_update: bool = False) -> None: ...
    async def restart_service(self) -> None: ...
    def get_update_status(self) -> dict[str, Any]: ...
    def get_persistent_data(self) -> dict[str, Any]: ...
