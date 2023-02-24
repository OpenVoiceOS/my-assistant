import mycroft.lock
from mycroft.skills.api import SkillApi
from mycroft.skills.core import FallbackSkill
from mycroft.skills.event_scheduler import EventScheduler
from mycroft.skills.intent_service import IntentService
from mycroft.util import (
    reset_sigint_handler,
    start_message_bus_client,
    wait_for_exit_signal, init_service_logger
)
from ovos_config.locale import setup_locale
from ovos_utils.log import LOG

from my_assistant.config import init_config_dir
from my_assistant.skills.skill_manager import MyAssistantSkillManager, on_error, on_stopping, on_ready, on_alive, \
    on_started


def main(alive_hook=on_alive, started_hook=on_started, ready_hook=on_ready,
         error_hook=on_error, stopping_hook=on_stopping, watchdog=None):
    """Create a thread that monitors the loaded skills, looking for updates

    Returns:
        SkillManager instance or None if it couldn't be initialized
    """
    init_config_dir()
    init_service_logger("skills")
    reset_sigint_handler()
    # Create PID file, prevent multiple instances of this service
    mycroft.lock.Lock('skills')

    setup_locale()

    # Connect this process to the Mycroft message bus
    bus = start_message_bus_client("SKILLS")
    _register_intent_services(bus)
    event_scheduler = EventScheduler(bus, autostart=False)
    event_scheduler.daemon = True
    event_scheduler.start()
    SkillApi.connect_bus(bus)
    skill_manager = MyAssistantSkillManager(bus, watchdog,
                                            alive_hook=alive_hook,
                                            started_hook=started_hook,
                                            stopping_hook=stopping_hook,
                                            ready_hook=ready_hook,
                                            error_hook=error_hook)

    skill_manager.start()

    wait_for_exit_signal()

    shutdown(skill_manager, event_scheduler)


def _register_intent_services(bus):
    """Start up the all intent services and connect them as needed.

    Args:
        bus: messagebus client to register the services on
    """
    service = IntentService(bus)
    # Register handler to trigger fallback system
    bus.on(
        'mycroft.skills.fallback',
        FallbackSkill.make_intent_failure_handler(bus)
    )
    return service


def shutdown(skill_manager, event_scheduler):
    LOG.info('Shutting down Skills service')
    if event_scheduler is not None:
        event_scheduler.shutdown()
    # Terminate all running threads that update skills
    if skill_manager is not None:
        skill_manager.stop()
        skill_manager.join()
    LOG.info('Skills service shutdown complete!')


if __name__ == "__main__":
    main()
