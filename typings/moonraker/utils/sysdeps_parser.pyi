from typing import Any

class SysDepsParser:
    distro_id: str
    aliases: list[str]
    distro_version: tuple[int | str, ...]
    vendor: str
    exclusions: list[str]
    def __init__(self, distro_info: dict[str, Any] | None = None) -> None: ...
    def parse_dependencies(self, sys_deps: dict[str, list[str]]) -> list[str]: ...
