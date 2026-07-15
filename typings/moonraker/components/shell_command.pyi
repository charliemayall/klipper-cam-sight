import asyncio
from ..confighelper import ConfigHelper as ConfigHelper
from ..utils import ServerError as ServerError
from _typeshed import Incomplete
from typing import Awaitable, Callable

OutputCallback = Callable[[bytes], None] | None

class ShellCommandError(ServerError):
    stdout: Incomplete
    stderr: Incomplete
    return_code: Incomplete
    def __init__(self, message: str, return_code: int | None, stdout: bytes | None = b'', stderr: bytes | None = b'', status_code: int = 500) -> None: ...

class ShellCommandProtocol(asyncio.subprocess.SubprocessStreamProtocol):
    std_out_cb: Incomplete
    std_err_cb: Incomplete
    log_stderr: Incomplete
    pending_data: list[bytes]
    def __init__(self, limit: int, loop: asyncio.events.AbstractEventLoop, std_out_cb: OutputCallback = None, std_err_cb: OutputCallback = None, log_stderr: bool = False) -> None: ...
    stdin: Incomplete
    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None: ...
    def pipe_data_received(self, fd: int, data: bytes | str) -> None: ...
    def pipe_connection_lost(self, fd: int, exc: Exception | None) -> None: ...

class ShellCommand:
    IDX_SIGINT: int
    IDX_SIGTERM: int
    IDX_SIGKILL: int
    factory: Incomplete
    name: Incomplete
    std_out_cb: Incomplete
    std_err_cb: Incomplete
    command: Incomplete
    log_stderr: Incomplete
    env: Incomplete
    cwd: Incomplete
    proc: asyncio.subprocess.Process | None
    cancelled: bool
    return_code: int | None
    run_lock: Incomplete
    def __init__(self, factory: ShellCommandFactory, cmd: str, std_out_callback: OutputCallback, std_err_callback: OutputCallback, env: dict[str, str] | None = None, log_stderr: bool = False, cwd: str | None = None) -> None: ...
    async def cancel(self, sig_idx: int = 1) -> None: ...
    def get_return_code(self) -> int | None: ...
    async def run(self, timeout: float = 2.0, verbose: bool = True, log_complete: bool = True, sig_idx: int = 1, proc_input: str | None = None, success_codes: list[int] | None = None) -> bool: ...
    async def run_with_response(self, timeout: float = 2.0, attempts: int = 1, log_complete: bool = True, sig_idx: int = 1, proc_input: str | None = None, success_codes: list[int] | None = None) -> str: ...

class ShellCommandFactory:
    error = ShellCommandError
    eventloop: Incomplete
    running_commands: set[ShellCommand]
    def __init__(self, config: ConfigHelper) -> None: ...
    def add_running_command(self, cmd: ShellCommand) -> None: ...
    def remove_running_command(self, cmd: ShellCommand) -> None: ...
    def build_shell_command(self, cmd: str, callback: OutputCallback = None, std_err_callback: OutputCallback = None, env: dict[str, str] | None = None, log_stderr: bool = False, cwd: str | None = None) -> ShellCommand: ...
    def run_cmd_async(self, cmd: str, callback: OutputCallback = None, std_err_callback: OutputCallback = None, timeout: float = 2.0, attempts: int = 1, verbose: bool = True, sig_idx: int = 1, proc_input: str | None = None, log_complete: bool = True, log_stderr: bool = False, env: dict[str, str] | None = None, cwd: str | None = None, success_codes: list[int] | None = None) -> Awaitable[None]: ...
    def exec_cmd(self, cmd: str, timeout: float = 2.0, attempts: int = 1, sig_idx: int = 1, proc_input: str | None = None, log_complete: bool = True, log_stderr: bool = False, env: dict[str, str] | None = None, cwd: str | None = None, success_codes: list[int] | None = None) -> Awaitable[str]: ...
    async def close(self) -> None: ...

def load_component(config: ConfigHelper) -> ShellCommandFactory: ...
