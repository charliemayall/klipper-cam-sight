from ...components.file_manager.file_manager import FileManager as FileManager
from ...confighelper import ConfigHelper as ConfigHelper
from ...utils import json_wrapper as json_wrapper, pip_utils as pip_utils
from ...utils.source_info import PackageInfo as PackageInfo, load_distribution_info as load_distribution_info, normalize_project_name as normalize_project_name
from ...utils.sysdeps_parser import SysDepsParser as SysDepsParser
from ...utils.versions import GitVersion as GitVersion, PyVersion as PyVersion
from .app_deploy import AppDeploy as AppDeploy, Channel as Channel
from _typeshed import Incomplete
from enum import Enum
from typing import Any

class PackageSource(Enum):
    PIP = 0
    GITHUB = 1
    UNKNOWN = 2

class PythonDeploy(AppDeploy):
    primary_branch: Incomplete
    project_name: Incomplete
    extras: str | None
    source: PackageSource
    repo_url: str
    repo_owner: str
    repo_name: str
    current_version: PyVersion
    git_version: GitVersion
    current_sha: str
    upstream_version: PyVersion
    upstream_sha: str
    rollback_version: PyVersion
    rollback_ref: str
    warnings: list[str]
    changelog: str
    system_deps: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def initialize(self) -> dict[str, Any]: ...
    def get_persistent_data(self) -> dict[str, Any]: ...
    def get_update_status(self) -> dict[str, Any]: ...
    async def refresh(self) -> None: ...
    async def update(self, rollback: bool = False) -> bool: ...
    async def recover(self, hard: bool = False, force_dep_update: bool = False) -> None: ...
    async def rollback(self) -> bool: ...
