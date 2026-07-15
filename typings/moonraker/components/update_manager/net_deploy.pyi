from ...confighelper import ConfigHelper as ConfigHelper
from ...utils import source_info as source_info
from ..file_manager.file_manager import FileManager as FileManager
from .app_deploy import AppDeploy as AppDeploy
from .common import AppType as AppType, Channel as Channel
from _typeshed import Incomplete
from typing import Any

class NetDeploy(AppDeploy):
    prefix: Incomplete
    repo: Incomplete
    asset_name: str | None
    persistent_files: list[str]
    warnings: list[str]
    anomalies: list[str]
    version: str
    remote_version: str
    rollback_version: str
    rollback_repo: str
    last_error: str
    def __init__(self, config: ConfigHelper) -> None: ...
    dl_info: Incomplete
    async def initialize(self) -> dict[str, Any]: ...
    def get_persistent_data(self) -> dict[str, Any]: ...
    async def refresh(self) -> None: ...
    async def update(self, rollback_info: tuple[str, str, int] | None = None, is_recover: bool = False, force_dep_update: bool = False) -> bool: ...
    async def recover(self, hard: bool = False, force_dep_update: bool = False) -> None: ...
    async def rollback(self) -> bool: ...
    def get_update_status(self) -> dict[str, Any]: ...
