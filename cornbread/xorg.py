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
    def __init__(self):
        self._log = logging.getLogger(".".join([__name__, "FocusedWindow"]))
        self._exit_watch = False
        self.__lock = threading.Lock()

    def get(self):
        self._log.debug("Returning copy")
        self.__lock.acquire()
        try:
            return copy(self)
        finally:
            self.__lock.release()

    def update(self, args):
        self._log.debug("Updating")
        self.__lock.acquire()
        try:
            self.__dict__.update(args)
        finally:
            self.__lock.release()
        self._log.warning(self.to_json())

    def to_json(self):
        return json.dumps({
            k: v
            for k, v in self.get().__dict__.items()
            if k[0] != '_'
        }, indent=4, sort_keys=True)
