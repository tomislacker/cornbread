"""
xorg
====

This module contains commands used for querying information from Xorg
"""
import json
import logging
import os
import threading
import Xlib
import Xlib.display
from copy import copy
from subprocess import Popen, PIPE

from .util import get_exe_by_pid


def _get_command_output(command):
    with Popen(command.split(' '), stdout=PIPE) as p:
        output, err = p.communicate()
    return output.decode('utf-8').strip()


def FocusedWindowWatcher(focused_window):
    log = logging.getLogger(".".join([__name__, "FocusedWindowWatcher"]))

    log.debug("Fetching display")
    disp = Xlib.display.Display()

    log.debug("Fetching display.screen().root")
    root = disp.screen().root

    net_wm_name = disp.intern_atom('_NET_WM_NAME')
    net_active_window = disp.intern_atom('_NET_ACTIVE_WINDOW')

    log.debug("Setting change mask")
    root.change_attributes(event_mask=Xlib.X.FocusChangeMask)

    log.debug("Entering event loop")
    while True:
        try:
            args = {}

            # Fetch the focused window ID
            args.update({
                'window_id': root.get_full_property(net_active_window, Xlib.X.AnyPropertyType).value[0],
            })

            # Fetch the window resource
            window = window = disp.create_resource_object('window', args['window_id'])

            window.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
            args.update({
                'window_name': window.get_full_property(net_wm_name, 0).value.decode('utf-8'),
            })

        except Xlib.error.XError:
            args.update({
                'window_name': None,
            })

        focused_window.update(args)
        event = disp.next_event()

        if focused_window._exit_watch == True:
            break


class FocusedWindow(object):
    @staticmethod
    def get_window_pid_by_id(window_id):
        return _get_command_output(
            "xdotool getwindowpid {}".format(window_id))

    def __init__(self):
        self._log = logging.getLogger(".".join([__name__, "FocusedWindow"]))
        self._exit_watch = False
        self.__lock = threading.Lock()

    def get(self, skip_lock=False):
        self._log.debug("Returning copy")
        if not skip_lock:
            self.__lock.acquire()

        try:
            return copy(self)
        finally:
            if not skip_lock:
                self.__lock.release()

    def update(self, args):
        self._log.debug("Updating")
        self.__lock.acquire()
        try:
            self.__dict__.update(args)
            self.__dict__.update({
                "pid": self.get_window_pid_by_id(self.window_id),
            })
            self.__dict__.update({
                "exe": get_exe_by_pid(self.pid),
            })
        finally:
            self._update_queue.put(self.get(skip_lock=True))
            self.__lock.release()

    def __eq__(self, other):
        try:
            return self.to_dict() == other.to_dict()
        except AttributeError:
            return False

    def to_dict(self):
        return {
            k: v
            for k, v in self.get().__dict__.items()
            if k[0] != '_'
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4, sort_keys=True)
