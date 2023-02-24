"""Load, update and manage skills on this device."""

from mycroft.skills.skill_manager import SkillManager
from ovos_utils.log import LOG


def on_started():
    LOG.info('Skills Manager is starting up.')


def on_alive():
    LOG.info('Skills Manager is alive.')


def on_ready():
    LOG.info('Skills Manager is ready.')


def on_error(e='Unknown'):
    LOG.info(f'Skills Manager failed to launch ({e})')


def on_stopping():
    LOG.info('Skills Manager is shutting down...')


class MyAssistantSkillManager(SkillManager):

    def __init__(self, bus, *args, **kwargs):
        """Constructor

        Args:
            bus (event emitter): Mycroft messagebus connection
        """
        super().__init__(bus, *args, **kwargs)
        # TODO - new awesome stuff
