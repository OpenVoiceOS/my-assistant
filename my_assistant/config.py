import importlib
import json
import os
from copy import deepcopy
from os.path import *

from ovos_utils.log import LOG
from ovos_utils.xdg_utils import xdg_config_home

ASSISTANT_CORE = "my_assistant"
CONF_FILE = f"{ASSISTANT_CORE}.conf"


def _init_ovos_conf(name: str, force_reload: bool = False):
    """
    Perform a one-time init of ovos.conf for the calling module
    :param name: Name of calling module to configure to use CONF_FILE
    :param force_reload: If true, force reload of configuration modules
    """
    from ovos_config.meta import get_ovos_config
    ovos_conf = get_ovos_config()
    original_conf = deepcopy(ovos_conf)
    ovos_conf.setdefault('module_overrides', {})
    ovos_conf.setdefault('submodule_mappings', {})

    if ASSISTANT_CORE not in ovos_conf['module_overrides']:
        ovos_conf['module_overrides'][ASSISTANT_CORE] = {
            "base_folder": ASSISTANT_CORE,
            "config_filename": CONF_FILE
        }

    if not ovos_conf.get('module_overrides', {}).get(ASSISTANT_CORE, {}).get("default_config_path"):
        try:
            default_config_path = join(dirname(__file__), CONF_FILE)
            ovos_conf["module_overrides"][ASSISTANT_CORE]["default_config_path"] = default_config_path
        except Exception as e:
            LOG.error(e)

    if name != "__main__" and name not in ovos_conf['submodule_mappings']:
        ovos_conf['submodule_mappings'][name] = ASSISTANT_CORE
        LOG.warning(f"Calling module ({name}) now configured to use CONF_FILE")
        if name == ASSISTANT_CORE:
            ovos_conf['submodule_mappings'][f'{ASSISTANT_CORE}.skills.skill_manager'] = ASSISTANT_CORE

        ovos_path = join(xdg_config_home(), "OpenVoiceOS", "ovos.conf")
        os.makedirs(dirname(ovos_path), exist_ok=True)
        config_to_write = {
            "module_overrides": ovos_conf.get('module_overrides'),
            "submodule_mappings": ovos_conf.get('submodule_mappings')
        }
        with open(ovos_path, "w+") as f:
            json.dump(config_to_write, f, indent=4)

    if force_reload or ovos_conf != original_conf:
        _force_module_reload()


def _force_module_reload():
    LOG.debug("Force reload of all configuration references")
    # Note that the below block reloads modules in a specific order due to
    # imports within ovos_config and mycroft.configuration
    import ovos_config
    importlib.reload(ovos_config.locations)

    from ovos_config.meta import get_ovos_config
    ovos_conf = get_ovos_config()  # Load the full stack for /etc overrides
    if ovos_conf["module_overrides"][ASSISTANT_CORE].get("default_config_path") \
            and ovos_config.locations.DEFAULT_CONFIG != \
            ovos_conf["module_overrides"][ASSISTANT_CORE]["default_config_path"]:
        ovos_config.locations.DEFAULT_CONFIG = \
            ovos_conf["module_overrides"][ASSISTANT_CORE]["default_config_path"]

        # Default config changed, remove any cached configuration
        del ovos_config.config.Configuration
        del ovos_config.Configuration

    import ovos_config.models
    importlib.reload(ovos_config.models)
    importlib.reload(ovos_config.config)
    importlib.reload(ovos_config)

    try:
        import mycroft.configuration
        import mycroft.configuration.locations
        import mycroft.configuration.config
        del mycroft.configuration.Configuration
        importlib.reload(mycroft.configuration.locations)
        importlib.reload(mycroft.configuration.config)
        importlib.reload(mycroft.configuration)
    except Exception as e:
        LOG.error(f"Failed to override mycroft.configuration: {e}")


def init_config_dir(force_reload=False):
    """
    Performs one-time initialization of the configuration directory.
    NOTE: This method is intended to be called once at module init, before any
    configuration is loaded. Repeated calls or calls after configuration is
    loaded may lead to inconsistent behavior.
    """
    import inspect

    stack = inspect.stack()
    mod = inspect.getmodule(stack[1][0])
    name = mod.__name__.split('.')[0] if mod else ''

    # Ensure `ovos.conf` specifies this module as using CONF_FILE
    _init_ovos_conf(name, force_reload)


def get_config_dir():
    """
    Get a default directory in which to find MyAssistant configuration files,
    creating it if it doesn't exist.
    Returns: Path to configuration or else default
    """
    config_path = join(xdg_config_home(), ASSISTANT_CORE)
    LOG.debug(config_path)
    if not isdir(config_path):
        LOG.info(f"Creating config directory: {config_path}")
        os.makedirs(config_path)
    return config_path
