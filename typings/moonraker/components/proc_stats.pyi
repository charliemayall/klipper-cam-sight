from ..common import RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from ..utils import ioctl_macros as ioctl_macros
from .websockets import WebsocketManager as WebsocketManager
from _typeshed import Incomplete
from typing import Any, Awaitable, Callable, Deque

STAT_CALLBACK = Callable[[int], Awaitable | None]
VC_GEN_CMD_FILE: str
VCIO_PATH: str
STATM_FILE_PATH: str
NET_DEV_PATH: str
TEMPERATURE_PATH: str
HWMON_ROOT_PATH: str
HWMON_PLATFORMS: Incomplete
CPU_STAT_PATH: str
MEM_AVAIL_PATH: str
STAT_UPDATE_TIME: float
REPORT_QUEUE_SIZE: int
THROTTLE_CHECK_INTERVAL: int
WATCHDOG_REFRESH_TIME: float
REPORT_BLOCKED_TIME: float
THROTTLED_FLAGS: Incomplete

class ProcStats:
    server: Incomplete
    event_loop: Incomplete
    watchdog: Incomplete
    stat_update_timer: Incomplete
    vcgencmd: VCGenCmd | None
    temp_file: Incomplete
    smaps: Incomplete
    netdev_file: Incomplete
    cpu_stats_file: Incomplete
    meminfo_file: Incomplete
    proc_stat_queue: Deque[dict[str, Any]]
    last_update_time: Incomplete
    last_proc_time: Incomplete
    throttle_check_lock: Incomplete
    total_throttled: int
    last_throttled: int
    update_sequence: int
    last_net_stats: dict[str, dict[str, Any]]
    last_cpu_stats: dict[str, tuple[int, int]]
    cpu_usage: dict[str, float]
    memory_usage: dict[str, int]
    stat_callbacks: list[STAT_CALLBACK]
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def register_stat_callback(self, callback: STAT_CALLBACK) -> None: ...
    def log_last_stats(self, count: int = 1): ...
    def close(self) -> None: ...

class Watchdog:
    proc_stats: Incomplete
    event_loop: Incomplete
    blocked_count: int
    last_watch_time: float
    watchdog_timer: Incomplete
    def __init__(self, proc_stats: ProcStats) -> None: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...

class VCGenCmd:
    MAX_STRING_SIZE: int
    GET_RESULT_CMD: int
    UINT_SIZE: Incomplete
    cmd_struct: Incomplete
    cmd_buf: Incomplete
    mailbox_req: Incomplete
    err_logged: bool
    def __init__(self) -> None: ...
    def run(self, cmd: str = 'get_throttled') -> str: ...

def load_component(config: ConfigHelper) -> ProcStats: ...
