"""Event queue management."""
import logging
from datetime import datetime
from threading import Event
from typing import List

from .const import APP_NAME

_LOGGER = logging.getLogger(APP_NAME)


class AppEvent:
    """Application event class."""

    def __init__(self):
        _LOGGER.debug("queuing event %s", type(self).__name__)
        event_queue.append(self)
        event_flag.set()


event_flag = Event()
event_queue: List[AppEvent] = []


class EventQueue:
    """Event queue."""

    def wait(self, sleep_interval) -> None:
        """Wait for an event."""
        sleep_start = datetime.now()
        _LOGGER.debug("sleeping for %ds", sleep_interval)
        event_flag.wait(timeout=sleep_interval)
        _LOGGER.debug(
            "woke up after %ds", (datetime.now() - sleep_start).total_seconds()
        )

    def pop(self) -> AppEvent | None:
        """Pop an event from the event queue."""
        if event_queue:
            return event_queue.pop(0)
        return None

    def check(self) -> bool:
        """Check whether event queue has events."""
        if event_flag.is_set():
            event_flag.clear()
            return True
        return False
