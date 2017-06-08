"""
util
====

This module contains random odds and ends to do things
"""
import os


def get_exe_by_pid(pid):
    if pid:
        return os.readlink(os.path.join("/proc", str(pid), "exe"))
    else:
        return None
