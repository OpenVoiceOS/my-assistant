from ovos_config.locale import setup_locale
from ovos_utils import wait_for_exit_signal
from ovos_utils.log import init_service_logger
from ovos_utils.process_utils import reset_sigint_handler, PIDLock

from my_assistant import init_config_dir
from my_assistant.listener.service import MyAssistantSpeechService, on_error, on_stopping, on_ready


def main(ready_hook=on_ready, error_hook=on_error, stopping_hook=on_stopping,
         watchdog=lambda: None):
    PIDLock("VOICE")
    init_config_dir()
    init_service_logger("voice")
    reset_sigint_handler()
    setup_locale()
    service = MyAssistantSpeechService(on_ready=ready_hook,
                                       on_error=error_hook,
                                       on_stopping=stopping_hook,
                                       watchdog=watchdog)
    service.daemon = True
    service.start()
    wait_for_exit_signal()


if __name__ == "__main__":
    main()
