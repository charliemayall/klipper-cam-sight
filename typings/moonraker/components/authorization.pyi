import asyncio
import ipaddress
from ..common import RequestType as RequestType, SqlTableDefinition as SqlTableDefinition, TransportType as TransportType, UserInfo as UserInfo, WebRequest as WebRequest
from ..confighelper import ConfigHelper as ConfigHelper
from .database import DBProviderWrapper as DBProviderWrapper
from .ldap import MoonrakerLDAP as MoonrakerLDAP
from .websockets import WebsocketManager as WebsocketManager
from _typeshed import Incomplete
from tornado.httputil import HTTPServerRequest as HTTPServerRequest
from typing import Any

IPAddr = ipaddress.IPv4Address | ipaddress.IPv6Address
IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network
OneshotToken = tuple[IPAddr, UserInfo | None, asyncio.Handle]

def base64url_encode(data: bytes) -> bytes: ...
def base64url_decode(data: str) -> bytes: ...

ONESHOT_TIMEOUT: int
TRUSTED_CONNECTION_TIMEOUT: int
FQDN_CACHE_TIMEOUT: int
PRUNE_CHECK_TIME: float
USER_TABLE: str
AUTH_SOURCES: Incomplete
HASH_ITER: int
API_USER: str
TRUSTED_USER: str
RESERVED_USERS: Incomplete
JWT_EXP_TIME: Incomplete
JWT_HEADER: Incomplete

class UserSqlDefinition(SqlTableDefinition):
    name = USER_TABLE
    prototype: Incomplete
    version: int
    def migrate(self, last_version: int, db_provider: DBProviderWrapper) -> None: ...

class Authorization:
    server: Incomplete
    login_timeout: Incomplete
    force_logins: Incomplete
    default_source: Incomplete
    enable_api_key: Incomplete
    max_logins: Incomplete
    failed_logins: dict[IPAddr, int]
    fqdn_cache: dict[IPAddr, dict[str, Any]]
    ldap: MoonrakerLDAP | None
    user_table: Incomplete
    users: dict[str, UserInfo]
    api_key: Incomplete
    issuer: Incomplete
    public_jwks: dict[str, dict[str, Any]]
    trusted_users: dict[IPAddr, dict[str, Any]]
    oneshot_tokens: dict[str, OneshotToken]
    cors_domains: list[str]
    trusted_ips: list[IPAddr]
    trusted_ranges: list[IPNetwork]
    trusted_domains: list[str]
    prune_timer: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def component_init(self) -> None: ...
    def decode_jwt(self, token: str, token_type: str = 'access', check_exp: bool = True) -> UserInfo: ...
    def validate_jwt(self, token: str) -> UserInfo: ...
    def validate_api_key(self, api_key: str) -> UserInfo: ...
    def get_oneshot_token(self, ip_addr: IPAddr, user: UserInfo | None) -> str: ...
    def check_logins_maxed(self, ip_addr: IPAddr) -> bool: ...
    async def authenticate_request(self, request: HTTPServerRequest, auth_required: bool = True) -> UserInfo | None: ...
    async def check_cors(self, origin: str | None) -> bool: ...
    def cors_enabled(self) -> bool: ...
    def get_api_key(self) -> str | None: ...
    def close(self) -> None: ...

def load_component(config: ConfigHelper) -> Authorization: ...
