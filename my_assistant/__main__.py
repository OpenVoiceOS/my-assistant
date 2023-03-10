from mycroft.audio.service import PlaybackService
from mycroft.gui.service import GUIService
from mycroft.messagebus.load_config import load_message_bus_config
from mycroft.messagebus.service.event_handler import MessageBusEventHandler
from mycroft.skills.api import SkillApi
from mycroft.skills.core import FallbackSkill
from mycroft.skills.event_scheduler import EventScheduler
from mycroft.skills.intent_service import IntentService
from mycroft_bus_client import MessageBusClient
from ovos_config.locale import setup_locale
from ovos_utils import (
    create_daemon
)
from ovos_utils import wait_for_exit_signal
from ovos_utils.log import LOG, init_service_logger
from ovos_utils.process_utils import reset_sigint_handler, PIDLock
from tornado import web, ioloop

from my_assistant import init_config_dir
from my_assistant.listener.service import SpeechService
from my_assistant.skills.skill_manager import MyAssistantSkillManager


def on_ready():
    LOG.info('Coach service started!')


def on_error(e='Unknown'):
    LOG.info('Coach failed to start ({})'.format(repr(e)))


def on_stopping():
    LOG.info('Coach is shutting down...')


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping):
    LOG.info('Starting My Assistant')

    init_config_dir()
    init_service_logger("my_assistant")
    reset_sigint_handler()
    PIDLock("my_assistant")
    setup_locale()

    # bus service
    LOG.info('Starting message bus service...')
    config = load_message_bus_config()
    routes = [(config.route, MessageBusEventHandler)]
    application = web.Application(routes)
    application.listen(config.port, config.host)

    # line below not needed because we run GUIService further down
    # create_daemon(ioloop.IOLoop.instance().start)

    # bus client
    bus = MessageBusClient()
    bus.run_in_thread()

    # GUI service
    LOG.info('Starting GUI bus service...')
    gui = GUIService()
    gui.run()

    # Audio output service
    LOG.info('Starting audio service...')
    audio = PlaybackService()
    audio.daemon = True
    audio.start()

    # STT service
    LOG.info('Starting STT service...')
    service = SpeechService()
    service.daemon = True
    service.start()

    # Skills service
    LOG.info('Starting Skills service...')
    intents = IntentService(bus)
    # Register handler to trigger fallback system
    bus.on(
        'mycroft.skills.fallback',
        FallbackSkill.make_intent_failure_handler(bus)
    )

    event_scheduler = EventScheduler(bus, autostart=False)
    event_scheduler.daemon = True
    event_scheduler.start()

    SkillApi.connect_bus(bus)

    skill_manager = MyAssistantSkillManager(bus)
    skill_manager.start()

    # wait until ctrl+c to exit
    ready_hook()
    wait_for_exit_signal()

    # shutdown cleanly
    audio.shutdown()
    gui.stop()
    if event_scheduler is not None:
        event_scheduler.shutdown()
    if skill_manager is not None:
        skill_manager.stop()
        skill_manager.join()
    stopping_hook()


if __name__ == "__main__":
    main()
