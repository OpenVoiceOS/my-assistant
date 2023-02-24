from mycroft.audio.service import PlaybackService, on_ready, on_error, on_stopping
from mycroft.lock import Lock as PIDLock  # Create/Support PID locking file
from mycroft.util import reset_sigint_handler, wait_for_exit_signal, \
    check_for_signal, init_service_logger
from ovos_config.locale import setup_locale

from my_assistant.config import init_config_dir


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping,
         watchdog=lambda: None):
    """Start the Audio Service and connect to the Message Bus"""
    init_config_dir()
    init_service_logger("audio")
    reset_sigint_handler()
    check_for_signal("isSpeaking")
    PIDLock("audio")
    setup_locale()
    service = PlaybackService(ready_hook=ready_hook, error_hook=error_hook,
                              stopping_hook=stopping_hook, watchdog=watchdog)
    service.daemon = True
    service.start()
    wait_for_exit_signal()
    service.shutdown()


if __name__ == '__main__':
    main()
