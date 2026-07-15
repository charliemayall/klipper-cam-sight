import asyncio
from ..common import JobEvent as JobEvent, RequestType as RequestType, UserInfo as UserInfo, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .file_manager.file_manager import FileManager as FileManager
from .job_state import JobState as JobState
from .klippy_apis import KlippyAPI as KlippyAPI
from _typeshed import Incomplete
from typing import Any

class JobQueue:
    server: Incomplete
    queued_jobs: dict[str, QueuedJob]
    lock: Incomplete
    pause_requested: bool
    load_on_start: Incomplete
    automatic: Incomplete
    queue_state: str
    job_delay: Incomplete
    job_transition_gcode: Incomplete
    pop_queue_handle: asyncio.TimerHandle | None
    def __init__(self, config: ConfigHelper) -> None: ...
    async def queue_job(self, filenames: str | list[str], check_exists: bool = True, reset: bool = False, user: UserInfo | None = None) -> None: ...
    async def delete_job(self, job_ids: str | list[str], all: bool = False) -> None: ...
    async def pause_queue(self) -> None: ...
    async def start_queue(self) -> None: ...
    async def close(self) -> None: ...

class QueuedJob:
    filename: Incomplete
    job_id: Incomplete
    time_added: Incomplete
    def __init__(self, filename: str, user: UserInfo | None = None) -> None: ...
    @property
    def user(self) -> UserInfo | None: ...
    def as_dict(self, cur_time: float) -> dict[str, Any]: ...

def load_component(config: ConfigHelper) -> JobQueue: ...
