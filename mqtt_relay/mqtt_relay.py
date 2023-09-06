"""Monitor file changes and publish contents to MQTT."""

import argparse
import logging
from pathlib import Path

from .const import APP_NAME, DEF_INOTIFY_TRIGGER_DELAY, DEF_INOTIFY_RESTART_DELAY
from .inotify import INotifyWatcher, INotifyEvent

from mqtt_base.mqtt_base import MQTTBaseApp
from mqtt_base.event import RefreshEvent
from mqtt_base.mqtt import MQTTConnectEvent
from mqtt_base.args import check_positive_int

_LOGGER = logging.getLogger(APP_NAME)


class MQTTRelayApp(MQTTBaseApp):
    APP_NAME = APP_NAME

    def __init__(self, args: dict):
        """Initialise MQTTRelayApp class."""
        super().__init__(args)

        self.path = Path(args["path"]).resolve(strict=False)
        self.inotify = INotifyWatcher(self.path, args)
        self.error_file_not_found = False
        self.payload_file_missing = args["payload_file_missing"]

    @classmethod
    def add_app_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--payload-file-missing",
            default=None,
            help="MQTT payload to publish if file is not found",
        )
        parser.add_argument(
            "--inotify-trigger-delay",
            type=check_positive_int,
            default=DEF_INOTIFY_TRIGGER_DELAY,
            help="Time in seconds to wait after file update is detected before publishing file",
        )
        parser.add_argument(
            "--inotify-restart-delay",
            type=check_positive_int,
            default=DEF_INOTIFY_RESTART_DELAY,
            help="Time in seconds to wait before restarting inotify watcher",
        )
        parser.add_argument(
            "path", help="Path to file whose contents are relayed to MQTT"
        )

    def setup(self, args) -> None:
        """Set up temperd app."""
        _LOGGER.info("setting up %s", self.APP_NAME)
        _LOGGER.debug("args: %s", args)
        self.inotify.start()

    def handle_event(self, event):
        """Handle temperd app event."""

        def publish_file() -> bool:
            try:
                payload = self.path.read_text().rstrip()
                self.error_file_not_found = False
            except FileNotFoundError as exc:
                if not self.error_file_not_found:
                    _LOGGER.error("%s", exc)
                    self.error_file_not_found = True
                    payload = self.payload_file_missing  ## default: remove topic
                else:
                    return False

            return self.publish_mqtt(
                self.mqtt_topic, payload, self.mqtt_qos, self.mqtt_retain
            )

        match event:
            case MQTTConnectEvent() | INotifyEvent() | RefreshEvent():
                publish_file()
            case _:
                _LOGGER.error("unknown event type %s", type(event).__name__)

    def shutdown(self):
        _LOGGER.info("shutting down %s", self.APP_NAME)
        if self.inotify:
            self.inotify.shutdown()


def main():
    MQTTRelayApp.main()


if __name__ == "__main__":
    main()
