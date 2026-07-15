from ..common import JobEvent as JobEvent, RequestType as RequestType, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .file_manager.file_manager import FileManager as FileManager
from _typeshed import Incomplete

class Notifier:
    server: Incomplete
    notifiers: dict[str, NotifierInstance]
    events: dict[str, list[NotifierInstance]]
    def __init__(self, config: ConfigHelper) -> None: ...
    def register_remote_actions(self) -> None: ...
    async def notify_action(self, name: str, message: str = ''): ...
    def register_endpoints(self, config: ConfigHelper): ...

class NotifierInstance:
    config: Incomplete
    server: Incomplete
    name: Incomplete
    apprise: Incomplete
    attach: Incomplete
    url: Incomplete
    title: Incomplete
    body: Incomplete
    body_format: Incomplete
    events: list[str]
    def __init__(self, config: ConfigHelper) -> None: ...
    def as_dict(self): ...
    async def notify(self, event_name: str, event_args: list, message: str = '') -> None: ...
    def get_name(self) -> str: ...

def load_component(config: ConfigHelper) -> Notifier: ...
