from mycroft.listener.service import SpeechService
from ovos_utils.log import LOG


def on_ready():
    LOG.info('Speech client is ready.')


def on_stopping():
    LOG.info('Speech service is shutting down...')


def on_error(e='Unknown'):
    LOG.error('Audio service failed to launch ({}).'.format(repr(e)))


class MyAssistantSpeechService(SpeechService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    # TODO awesome stuff
