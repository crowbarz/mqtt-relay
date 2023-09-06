"""inotify watcher class."""

import logging
import os
import select
import time
import traceback
from pathlib import Path
from threading import Thread

import inotify_simple as inotify
from mqtt_base.event import AppEvent

from .const import APP_NAME

_LOGGER = logging.getLogger(APP_NAME)

DEF_INOTIFY_FLAGS = (  # when watching file
    inotify.flags.ATTRIB
    | inotify.masks.MOVE
    | inotify.flags.DELETE_SELF
    | inotify.flags.MOVE_SELF
    | inotify.flags.MODIFY
)
DEF_INOTIFY_FLAGS_PARENT = (  # when watching parent directory
    inotify.flags.CREATE
    | inotify.flags.DELETE
    | inotify.flags.DELETE_SELF
    | inotify.flags.MOVE_SELF
)
DEF_INOTIFY_FLAGS_RESTART = (  # re-create inotify watcher
    inotify.flags.ATTRIB
    | inotify.masks.MOVE
    | inotify.flags.CREATE
    | inotify.flags.DELETE
    | inotify.flags.DELETE_SELF
    | inotify.flags.MOVE_SELF
)


class INotifyEvent(AppEvent):
    """Event class for inotify event."""


class INotifyShutdown(Exception):
    """Exception class for inotify thread shutdown."""


class INotifyWatcher(Thread):
    """Watch a file using inotify."""

    def __init__(self, path: Path, args: dict):
        self.__path = path
        self.__trigger_delay = args["inotify_trigger_delay"]
        self.__restart_delay = args["inotify_restart_delay"]

        self.__wd = None
        self.__wd_path = None
        self.__watch_parent = False
        self.__inotify = None

        self.__read_fd = None
        self.__write = None

        super().__init__()

    def cleanup(self):
        """Clean up inotify watcher."""
        _LOGGER.info("cleaning up watcher")
        if self.__inotify:
            self.__inotify.close()
            del self.__inotify
        self.__wd = None
        self.__wd_path = None
        self.__watch_parent = False

    def setup(self):
        """Set up inotify watcher."""
        _LOGGER.info("setting up watcher")
        self.__inotify = inotify.INotify()
        try:
            if not (self.__path.is_file() and os.access(self.__path, os.R_OK)):
                raise FileNotFoundError
            self.__wd = self.__inotify.add_watch(self.__path, DEF_INOTIFY_FLAGS)
            if self.__wd:
                self.__wd_path = self.__path
                _LOGGER.info("watching file path %s", self.__path)
            return
        except FileNotFoundError as exc:
            pass
        except Exception as exc:
            self.__wd = None
            self.__wd_path = None
            raise Exception("could not watch path %s: %s", self.__path, exc) from exc

        ## Watch parent directory if file does not exist
        parent_path = self.__path.parent
        try:
            self.__wd = self.__inotify.add_watch(parent_path, DEF_INOTIFY_FLAGS_PARENT)
            if self.__wd:
                self.__wd_path = parent_path
                self.__watch_parent = True
                _LOGGER.info("watching parent directory %s", parent_path)
        except Exception as exc:
            self.__wd = None
            raise Exception(
                "could not watch parent path %s: %s", parent_path, exc
            ) from exc

    def trigger_update(self):
        """Trigger an event when inotify notifies that the file has been updated."""
        _LOGGER.debug("file change detected, triggering event")
        INotifyEvent()

    def main_loop(self):
        """Process inotify events and trigger an event when the file has been updated."""
        read_delay = 0 if self.__watch_parent else self.__trigger_delay

        ## https://inotify-simple.readthedocs.io/en/latest/
        rlist, _, _ = select.select([self.__inotify.fileno(), self.__read_fd], [], [])

        if self.__inotify.fileno() in rlist:
            events = self.__inotify.read(read_delay=read_delay)
            update = False
            restart = False
            for event in events:
                (wd, mask, cookie, name) = event
                flags = ", ".join([str(flag) for flag in inotify.flags.from_mask(mask)])
                _LOGGER.debug("Event(%s, [%s], %s, %s)", wd, flags, cookie, name)
                update = True
                if mask & DEF_INOTIFY_FLAGS_RESTART:
                    restart = True  ## set up inotify listener again
            if update:
                self.trigger_update()
            return not restart

        ## Thread shutdown requested
        raise INotifyShutdown

    def run(self):
        """Set up inotify thread and run main loop."""
        ## Create a pipe for signalling shutdown
        self.__read_fd, write_fd = os.pipe()
        self.__write = os.fdopen(write_fd, "wb")
        self.setup()

        while True:
            try:
                if self.main_loop():
                    continue
            except INotifyShutdown:
                _LOGGER.info("shutting down watcher")
                self.cleanup()
                os.close(self.__read_fd)
                return
            except Exception as exc:
                _LOGGER.error("watcher exception: %s", exc)
                traceback.print_exc()

            ## Restart inotify watcher
            self.cleanup()
            _LOGGER.info("restarting watcher after %ds delay", self.__restart_delay)
            time.sleep(self.__restart_delay)
            self.setup()

    def shutdown(self):
        """Shut down the inotify watcher thread."""
        ## Request shutdown by writing in the pipe
        if not self.__write.closed:
            self.__write.write(b"\x00")
            self.__write.close()
