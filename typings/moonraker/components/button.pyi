from ..confighelper import ConfigHelper as ConfigHelper
from .application import InternalTransport as ITransport
from _typeshed import Incomplete
from typing import Any

class ButtonManager:
    server: Incomplete
    buttons: dict[str, GpioButton]
    def __init__(self, config: ConfigHelper) -> None: ...
    def component_init(self) -> None: ...

class GpioButton:
    server: Incomplete
    eventloop: Incomplete
    name: Incomplete
    itransport: ITransport
    mutex: Incomplete
    gpio_event: Incomplete
    min_event_time: Incomplete
    press_template: Incomplete
    release_template: Incomplete
    notification_sent: bool
    user_data: dict[str, Any]
    context: dict[str, Any]
    def __init__(self, config: ConfigHelper) -> None: ...
    def initialize(self) -> None: ...
    def get_status(self) -> dict[str, Any]: ...

def load_component(config: ConfigHelper) -> ButtonManager: ...
