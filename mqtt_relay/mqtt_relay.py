"""Monitor file changes and publish contents to MQTT."""

import logging
import signal
import traceback
import sys
from pathlib import Path

import daemon
from daemon import pidfile

from .args import parse_args
from .const import APP_NAME
from .exception import ExitApp
from .event import EventQueue
from .inotify import INotifyWatcher, INotifyEvent
from .mqtt import MQTTClient, MQTTConnectEvent

_LOGGER = logging.getLogger(APP_NAME)


# def get_backoff_delay(retry_count, delay_max):
#     """Calculate exponential backoff with random jitter delay."""
#     delay = round(
#         min(delay_max, (2**retry_count)) - (random.randint(0, 1000) / 1000),
#         3,
#     )
#     return delay


class MQTTRelayApp:
    def __init__(self, args: dict):
        """Initialise MQTTRelayApp class."""

        self.event_queue = EventQueue()  ## Initialise event queue
        self.mqtt_client = MQTTClient(args)  ## Initialise MQTT client
        self.path = Path(args["path"]).resolve(strict=False)
        self.inotify = INotifyWatcher(
            self.path, args
        )  ## Initialise inotify watcher thread

        self.mqtt_host = args["host"]
        self.mqtt_port = args["port"]
        self.mqtt_keepalive = args["keepalive"]

        self.mqtt_topic = args["topic"]
        self.mqtt_qos = args["qos"]
        self.mqtt_retain = args["retain"]
        self.connect_timeout = args["connect_timeout"]
        self.refresh_interval = args["refresh_interval"]

    def main_loop(self, args):
        """Main application loop."""
        self.inotify.start()

        ## Connect to MQTT broker
        mqtt_client = self.mqtt_client
        _LOGGER.info("connecting to MQTT broker %s:%d", self.mqtt_host, self.mqtt_port)
        mqtt_client.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive)

        mqtt_connected = False
        event_queue = self.event_queue
        sleep_interval = self.connect_timeout

        def publish_file() -> bool:
            return mqtt_client.publish_file(
                self.path, self.mqtt_topic, self.mqtt_qos, self.mqtt_retain
            )

        while True:
            event_queue.wait(sleep_interval)
            if event_queue.check():
                while event := event_queue.pop():
                    _LOGGER.debug("processing event %s", type(event).__name__)
                    match event:
                        case MQTTConnectEvent():
                            if event.rc == 0:
                                mqtt_connected = True
                                publish_file()
                        case INotifyEvent():
                            publish_file()
                        case _:
                            _LOGGER.error("unknown event type %s", type(event).__name__)
            elif mqtt_connected:  ## waited for refresh_interval
                publish_file()
            else:
                raise Exception("connection to MQTT broker timed out")
            sleep_interval = self.refresh_interval

    def shutdown(self):
        _LOGGER.info("shutting down %s", APP_NAME)
        if self.inotify:
            self.inotify.shutdown()

        if self.mqtt_client:
            self.mqtt_client.shutdown()


def setup_logging(log_level_count: int, logfile: str | None):
    log_level = logging.WARNING
    log_level_name = "default"
    if log_level_count >= 2:
        log_level = logging.DEBUG
        log_level_name = "debug"
    elif log_level_count >= 1:
        log_level = logging.INFO
        log_level_name = "info"

    ## Enable logging
    log_format = "%(asctime)s %(levelname)s: %(message)s"
    log_format_color = "%(log_color)s" + log_format
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        import colorlog

        colorlog.basicConfig(
            filename=logfile,
            level=log_level,
            format=log_format_color,
            datefmt=date_format,
        )
    except:
        logging.basicConfig(
            filename=logfile, level=log_level, format=log_format, datefmt=date_format
        )
    _LOGGER.info("setting log level to %s", log_level_name)


def main():
    """Main application."""
    args = parse_args()
    try:
        app = MQTTRelayApp(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        exit(255)

    debug = args["debug"]
    logfile = args["logfile"]

    def sigterm_handler(_signal, _frame):
        _LOGGER.warning("SIGTERM received, exiting")
        raise ExitApp(0)

    def start():
        try:
            rc = 0
            signal.signal(signal.SIGTERM, sigterm_handler)
            app.main_loop(args)
        except KeyboardInterrupt:
            _LOGGER.warning("Keyboard interrupt, exiting")
        except ExitApp as exc:
            rc = exc.rc
        except Exception as exc:
            _LOGGER.error(f"Exception: %s", exc)
            traceback.print_exc()
            rc = 255
        finally:
            app.shutdown()
        exit(rc)

    if args["daemon"]:
        pid_file = args["pidfile"]
        pid_lock = pidfile.TimeoutPIDLockFile(pid_file) if pid_file else None
        with daemon.DaemonContext(pidfile=pid_lock):
            setup_logging(debug, logfile)
            _LOGGER.info("starting %s as daemon", APP_NAME)
            start()
    else:
        setup_logging(debug, logfile)
        start()


if __name__ == "__main__":
    main()
