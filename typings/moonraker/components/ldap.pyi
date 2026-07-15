from ..confighelper import ConfigHelper as ConfigHelper
from _typeshed import Incomplete
from ldap3.abstract.entry import Entry as Entry

VALID_MEMBERSHIP_ATTRS: Incomplete

class MoonrakerLDAP:
    server: Incomplete
    ldap_host: Incomplete
    ldap_port: Incomplete
    ldap_secure: Incomplete
    membership_attr: Incomplete
    check_dn_case: Incomplete
    base_dn: Incomplete
    group_dn: str | None
    active_directory: Incomplete
    bind_dn: str | None
    bind_password: str | None
    user_filter: str | None
    lock: Incomplete
    def __init__(self, config: ConfigHelper) -> None: ...
    async def authenticate_ldap_user(self, username: str, password: str) -> None: ...

def load_component(config: ConfigHelper) -> MoonrakerLDAP: ...
