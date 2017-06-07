"""
xorg
====

This module contains commands used for querying information from Xorg
"""
import json
import os
from subprocess import Popen, PIPE

def _get_command_output(command):
    with Popen(command.split(' '), stdout=PIPE) as p:
        output, err = p.communicate()
    return output.decode('utf-8').strip()


class FocusedWindow(object):
    @classmethod
    def get(cls):
        return cls()

    @staticmethod
    def _get_focused_window_name():
        return _get_command_output("xdotool getwindowfocus getwindowname")

    @staticmethod
    def _get_focused_window_id():
        return _get_command_output("xdotool getactivewindow")

    @staticmethod
    def _get_window_pid(window_id):
        return _get_command_output(
            "xdotool getwindowpid {}".format(window_id))

    @staticmethod
    def _get_focused_window_pid():
        return get_window_pid(get_focused_window_id())

    @staticmethod
    def _get_focused_window_exe():
        return get_pid_exe(get_focused_window_pid())

    @staticmethod
    def _get_pid_exe(pid):
        return os.readlink("/proc/{}/exe".format(pid))

    def __init__(self):
        self.window_name = self._get_focused_window_name()
        self.window_id = self._get_focused_window_id()
        self.window_pid = self._get_window_pid(self.window_id)
        self.window_exe = self._get_pid_exe(self.window_pid)

    def to_json(self, **args):
        base_args = {
            'indent': 4,
            'sort_keys': True,
        }
        base_args.update(args)

        return json.dumps(
            {
                v: getattr(self, v)
                for v in [
                    'window_name',
                    'window_id',
                    'window_pid',
                    'window_exe'
                ]
            },
            **base_args
        )
