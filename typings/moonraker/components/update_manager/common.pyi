import pathlib
from ...common import ExtendedEnum as ExtendedEnum
from ...confighelper import ConfigHelper as ConfigHelper
from ...utils import source_info as source_info
from ..klippy_connection import KlippyConnection as KlippyConnection
from _typeshed import Incomplete

BASE_CONFIG: dict[str, dict[str, str]]
OPTION_OVERRIDES: Incomplete

class AppType(ExtendedEnum):
    NONE = 1
    WEB = 2
    GIT_REPO = 3
    ZIP = 4
    PYTHON = 5
    EXECUTABLE = 6
    @classmethod
    def detect(cls, app_path: str | pathlib.Path | None = None): ...
    @classmethod
    def valid_types(cls) -> list[AppType]: ...
    @property
    def supported_channels(self) -> list[Channel]: ...
    @property
    def default_channel(self) -> Channel: ...

class Channel(ExtendedEnum):
    STABLE = 1
    BETA = 2
    DEV = 3

def get_base_configuration(config: ConfigHelper) -> ConfigHelper: ...
