from ..common import JobEvent as JobEvent, KlippyState as KlippyState
from ..confighelper import ConfigHelper as ConfigHelper
from .klippy_apis import KlippyAPI as KlippyAPI
from _typeshed import Incomplete
from typing import Any

class JobState:
    server: Incomplete
    last_print_stats: dict[str, Any]
    last_event: JobEvent
    def __init__(self, config: ConfigHelper) -> None: ...
    def get_last_stats(self) -> dict[str, Any]: ...
    def get_last_job_event(self) -> JobEvent: ...

def load_component(config: ConfigHelper) -> JobState: ...
