"""
cornbread - Daemon to track your window focus

Usage:
    cornbread daemon [options]
    cornbread process [options]

Options:
    -h, --help          See this dialogue
    -l, --log-level=L   Logging module level [default: debug]
    -v, --version       See program version
"""
import logging
import time
from queue import Queue
from threading import Condition
from threading import Thread

from . import __version__
from .xorg import FocusedWindow
from .xorg import FocusedWindowWatcher


log = logging.getLogger("cornbread")


class ObjectBuffer(object):
    def __init__(self):
        self.condition = Condition()
        self.objects = []

    def __len__(self):
        with self.condition:
            return len(self.objects)

    def put(self, obj):
        with self.condition:
            self.objects.append(obj)
            self.condition.notify()

    def pop_all(self):
        with self.condition:
            objects, self.objects = self.objects, []
        return objects


def JSONLineBufferWriter(obj_buffer, jsonl_file, flush_size=20,
                         flush_seconds=5):
    while True:
        if len(obj_buffer) < flush_size:
            time.sleep(flush_seconds)
        objs = obj_buffer.pop_all()

        if not any(objs):
            log.debug("JSONLineBufferWriter - re-polling")
            time.sleep(flush_seconds)
            continue

        log.info("JSONLineBufferWriter - writing {c} entr{s} to {f}".format(
            c=len(objs),
            s="ies" if len(objs) != 1 else "y",
            f=jsonl_file))

        with open(jsonl_file, "a") as out_file:
            for obj in objs:
                out_file.write(obj.to_json() + "\n")


def OnFocusUpdate(focus_queue, focus_buffer):
    old_focus = None
    while True:
        new_focus = focus_queue.get()

        # Check if focus actually changed
        if new_focus == old_focus:
            continue

        # Payload to execute (write to disk?)
        log.info("Focus update:\n" + new_focus.to_json())
        focus_buffer.put(new_focus)

        # Remember previous focus
        old_focus = new_focus


def daemon():
    log.warning("Starting daemon")
    focus_update_queue = Queue()
    focused_window = FocusedWindow(focus_update_queue)

    focus_buffer = ObjectBuffer()

    log.info("Starting focus_buffer_writer")
    focus_buffer_writer = Thread(target=JSONLineBufferWriter,
                                 args=(
                                     focus_buffer,
                                     "/tmp/cornbread-focus.jsonl",
                                     20, # Buffer size
                                     5,  # Seconds between flushes
                                 ))
    focus_buffer_writer.setDaemon(True)
    focus_buffer_writer.start()

    log.info("Starting focus_update_thread")
    focus_update_thread = Thread(target=OnFocusUpdate,
                                 args=(focus_update_queue,focus_buffer))
    focus_update_thread.setDaemon(True)
    focus_update_thread.start()

    # Start focus-update watche
    log.info("Starting focus_watch_thread")
    focus_watch_thread = Thread(target=FocusedWindowWatcher,
                                args=(focused_window, focus_update_queue,))
    focus_watch_thread.setDaemon(True)
    focus_watch_thread.start()

    try:
        focus_watch_thread.join()

    except KeyboardInterrupt:
        log.warning("Stopping focus_watch_thread")
        focus_watch_thread.join(1)
        log.warning("Stopping focus_update_thread")
        focus_update_thread.join(1)
        log.warning("Stopping focus_buffer_writer")
        focus_buffer_writer.join(5)


def entrypoint():
    from docopt import docopt
    args = docopt(__doc__, version=__version__)

    logging.basicConfig(**{
        "level": getattr(logging, args['--log-level'].upper()),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    })

    import json
    log.debug(":\n" + json.dumps(args, indent=4, sort_keys=True))

    if args['daemon']:
        daemon()

    elif args['process']:
        raise NotImplementedError


if __name__ == '__main__':
    entrypoint()
