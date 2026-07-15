from . import update_manager as um
from ...confighelper import ConfigHelper

def load_component(config: ConfigHelper) -> um.UpdateManager: ...
