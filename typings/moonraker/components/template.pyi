import jinja2
from ..common import RenderableTemplate as RenderableTemplate
from ..confighelper import ConfigHelper as ConfigHelper
from ..server import Server as Server
from .secrets import Secrets as Secrets
from _typeshed import Incomplete
from typing import Any

class TemplateFactory:
    server: Incomplete
    jenv: Incomplete
    async_env: Incomplete
    ui_env: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    def add_environment_global(self, name: str, value: Any): ...
    def create_template(self, source: str, is_async: bool = False) -> JinjaTemplate: ...
    def create_ui_template(self, source: str) -> JinjaTemplate: ...

class JinjaTemplate(RenderableTemplate):
    server: Incomplete
    orig_source: Incomplete
    template: Incomplete
    is_async: Incomplete
    def __init__(self, source: str, server: Server, template: jinja2.Template, is_async: bool) -> None: ...
    def render(self, context: dict[str, Any] = {}) -> str: ...
    async def render_async(self, context: dict[str, Any] = {}) -> str: ...

def load_component(config: ConfigHelper) -> TemplateFactory: ...
